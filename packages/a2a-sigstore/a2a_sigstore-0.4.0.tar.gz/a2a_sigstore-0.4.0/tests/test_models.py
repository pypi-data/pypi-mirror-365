import pytest
from a2a.types import AgentCard
from pydantic import ValidationError

from a2a_sigstore.models.provenance import DigestSet, ProvenanceSubject
from a2a_sigstore.models.signature import SignatureBundle


class TestAgentCard:
    """Test Agent Card model validation."""

    def test_agent_card_validation(self):
        """Test basic Agent Card validation."""
        card_data = {
            "protocolVersion": "0.2.9",
            "name": "Test Agent",
            "description": "A test agent",
            "url": "https://example.com/agent",
            "version": "1.0.0",
            "capabilities": {"streaming": True, "pushNotifications": False},
            "defaultInputModes": ["application/json"],
            "defaultOutputModes": ["application/json"],
            "skills": [{"id": "test-skill", "name": "Test Skill", "description": "A test skill", "tags": ["test"]}],
        }

        card = AgentCard.model_validate(card_data)
        assert card.name == "Test Agent"
        assert card.version == "1.0.0"
        assert len(card.skills) == 1

    def test_agent_card_with_provider(self):
        """Test Agent Card with provider information."""
        card_data = {
            "protocolVersion": "0.2.9",
            "name": "Test Agent",
            "description": "A test agent",
            "url": "https://example.com/agent",
            "version": "1.0.0",
            "provider": {"organization": "Test Org", "url": "https://example.com"},
            "capabilities": {},
            "defaultInputModes": ["application/json"],
            "defaultOutputModes": ["application/json"],
            "skills": [],
        }

        card = AgentCard.model_validate(card_data)
        assert card.provider is not None
        assert card.provider.organization == "Test Org"

    def test_agent_card_missing_required_fields(self):
        """Test Agent Card validation with missing required fields."""
        card_data = {
            "name": "Test Agent"
            # Missing required fields
        }

        with pytest.raises(ValidationError):
            AgentCard.model_validate(card_data)


class TestProvenance:
    """Test SLSA provenance models."""

    def test_provenance_subject(self):
        """Test provenance subject creation."""
        subject = ProvenanceSubject(name="test-agent", digest=DigestSet(sha256="abc123", sha1="def456"))

        assert subject.name == "test-agent"
        assert subject.digest.sha256 == "abc123"

    def test_digest_set(self):
        """Test digest set validation."""
        digest = DigestSet(sha256="test-hash")
        assert digest.sha256 == "test-hash"
        assert digest.sha1 is None


class TestSignature:
    """Test signature and bundle models."""

    def test_signature_bundle(self):
        """Test signature bundle creation."""
        from datetime import datetime

        bundle = SignatureBundle(signature="test-signature", certificate="test-cert", timestamp=datetime.utcnow())

        assert bundle.signature == "test-signature"
        assert bundle.certificate == "test-cert"
