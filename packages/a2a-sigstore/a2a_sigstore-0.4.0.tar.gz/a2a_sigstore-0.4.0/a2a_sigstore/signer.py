import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from a2a.types import AgentCard
from sigstore.dsse import DigestSet, StatementBuilder, Subject
from sigstore.oidc import IdentityToken, Issuer, detect_credential
from sigstore.sign import SigningContext

from .models.provenance import SLSAProvenance
from .models.signature import SignatureBundle, SignedAgentCard, VerificationMaterial
from .utils.crypto import canonicalize_json


class AgentCardSigner:
    """Signs A2A Agent Cards using Sigstore keyless signing."""

    def __init__(self, issuer: Issuer | None = None, identity_token: str | None = None, staging: bool = False):
        """Initialize the Agent Card signer.

        Args:
            issuer: OIDC issuer for authentication
            identity_token: Pre-obtained identity token
            staging: Use Sigstore staging environment
        """
        self.issuer = issuer
        self.identity_token = identity_token
        self.staging = staging
        self._signer: SigningContext | None = None

    def _get_signer(self) -> SigningContext:
        """Get or create a Sigstore signer instance."""
        if self._signer is None:
            if self.staging:
                self._signer = SigningContext.production()  # Will use staging when available
            else:
                self._signer = SigningContext.production()

        return self._signer

    def sign_agent_card(
        self, agent_card: AgentCard | dict[str, Any] | str | Path, provenance_bundle: SLSAProvenance | None = None
    ) -> SignedAgentCard:
        """Sign an A2A Agent Card.

        Args:
            agent_card: Agent card to sign (model, dict, JSON string, or file path)
            provenance_bundle: Optional SLSA provenance bundle

        Returns:
            Signed Agent Card with verification material

        Raises:
            ValueError: If agent card is invalid
            RuntimeError: If signing fails
        """
        if isinstance(agent_card, str | Path):
            if Path(agent_card).exists():
                with open(agent_card) as f:
                    card_data = json.load(f)
            else:
                card_data = json.loads(str(agent_card))
        elif isinstance(agent_card, dict):
            card_data = agent_card
        elif isinstance(agent_card, AgentCard):
            card_data = agent_card.model_dump(by_alias=True)
        else:
            raise ValueError(f"Invalid agent card type: {type(agent_card)}")
        try:
            parsed_card = AgentCard.model_validate(card_data)
        except Exception as e:
            raise ValueError(f"Invalid agent card: {e}") from e

        canonical_data = canonicalize_json(card_data)

        # Create in-toto statement for agent card
        import hashlib

        # Calculate digest of the canonical data
        digest_hex = hashlib.sha256(canonical_data).hexdigest()
        digest_set = DigestSet(root={"sha256": digest_hex})

        # Create subject for the agent card
        subject = Subject(name=parsed_card.name, digest=digest_set)

        # Build the in-toto statement
        builder = StatementBuilder()
        builder = builder.subjects([subject])
        builder = builder.predicate_type("https://a2a.openwallet.dev/agentcard/v1")
        builder = builder.predicate(card_data)

        # Build the statement
        statement = builder.build()

        signing_context = self._get_signer()

        try:
            # Detect ambient credential (returns string token or None)
            ambient_credential = detect_credential()

            if ambient_credential:
                # Wrap ambient credential in IdentityToken object
                identity = IdentityToken(ambient_credential)
                with signing_context.signer(identity, cache=True) as signer:
                    bundle = signer.sign_dsse(statement)
            elif self.identity_token:
                # Use provided identity token (wrap if string)
                if isinstance(self.identity_token, str):
                    identity = IdentityToken(self.identity_token)
                else:
                    identity = self.identity_token
                with signing_context.signer(identity, cache=True) as signer:
                    bundle = signer.sign_dsse(statement)
            else:
                # Fallback to interactive flow
                issuer = self.issuer or Issuer.production()
                identity = issuer.identity_token()
                with signing_context.signer(identity, cache=True) as signer:
                    bundle = signer.sign_dsse(statement)
        except Exception as e:
            raise RuntimeError(f"Failed to sign agent card: {e}") from e

        # Extract transparency log entry if present
        log_entry_dict = None
        if hasattr(bundle, "log_entry") and bundle.log_entry:
            # Convert LogEntry to dictionary representation
            try:
                # LogEntry should have a model_dump method or be serializable
                if hasattr(bundle.log_entry, "model_dump"):
                    log_entry_dict = bundle.log_entry.model_dump()
                elif hasattr(bundle.log_entry, "to_dict"):
                    log_entry_dict = bundle.log_entry.to_dict()
                else:
                    # Fallback: try to extract basic fields
                    log_entry_dict = {
                        "log_index": getattr(bundle.log_entry, "log_index", None),
                        "log_id": getattr(bundle.log_entry, "log_id", None),
                        "integrated_time": getattr(bundle.log_entry, "integrated_time", None),
                    }
            except Exception as e:
                print(f"Error extracting log entry: {e}")
                # If we can't extract log entry details, still include the fact that it exists
                log_entry_dict = {"present": True}

        # Store the bundle with extracted transparency log entry
        signature_bundle = SignatureBundle(
            signature=bundle.to_json(),  # Store entire bundle as JSON
            certificate="",  # Certificate is included in the bundle JSON
            certificate_chain=None,  # Chain is included in the bundle JSON
            transparency_log_entry=log_entry_dict,
            timestamp=datetime.now(timezone.utc),
        )

        verification_material = VerificationMaterial(
            signature_bundle=signature_bundle, provenance_bundle=provenance_bundle
        )

        signed_card = SignedAgentCard(agent_card=parsed_card, verification_material=verification_material)

        return signed_card

    def sign_file(
        self,
        input_path: str | Path,
        output_path: str | Path | None = None,
        provenance_bundle: SLSAProvenance | None = None,
    ) -> Path:
        """Sign an Agent Card file.

        Args:
            input_path: Path to Agent Card JSON file
            output_path: Output path for signed card (default: input_path with .signed.json)
            provenance_bundle: Optional SLSA provenance bundle

        Returns:
            Path to signed Agent Card file
        """
        input_path = Path(input_path)

        if output_path is None:
            output_path = input_path.with_suffix(".signed.json")
        else:
            output_path = Path(output_path)

        signed_card = self.sign_agent_card(input_path, provenance_bundle)

        with open(output_path, "w") as f:
            json.dump(signed_card.model_dump(by_alias=True), f, indent=2, default=str)

        return output_path
