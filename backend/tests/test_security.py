"""
MailTrace AI — Security Foundation Unit Tests

Tests all 5 security modules on feature/security-foundation:
- HeaderForensics (Received chain parsing, originating IP, spoofing detection)
- AuthenticationAnalyzer (SPF/DKIM/DMARC evaluation and UNKNOWN states)
- EvidencePreserver (ISO/IEC 27037 SHA-256 hashing & custody chain)
- PIIRedactor (Aadhaar/PAN masking & AES-256 encryption)
- SecurityPolicyEngine (Delivery policy decision logic)
"""

import unittest
from backend.analysis.header_forensics import HeaderForensics
from backend.analysis.authentication import AuthenticationAnalyzer, AuthStatus
from backend.analysis.evidence_preservation import EvidencePreserver
from backend.analysis.pii_redaction import PIIRedactor
from backend.analysis.security_policy import SecurityPolicyEngine, RiskLevel, DeliveryAction


class TestSecurityFoundation(unittest.TestCase):

    def setUp(self):
        self.header_forensics = HeaderForensics()
        self.auth_analyzer = AuthenticationAnalyzer()
        self.evidence_preserver = EvidencePreserver()
        self.pii_redactor = PIIRedactor()
        self.policy_engine = SecurityPolicyEngine()

    def test_legitimate_email_headers(self):
        sample_legit_email = (
            "Received: from mail-pj1-f41.google.com ([209.85.216.41])\r\n"
            "        by mx.google.com with SMTPS id x123so123456pjb.1\r\n"
            "        for <recipient@sih.gov.in>; Thu, 10 Sep 2026 10:00:00 -0700\r\n"
            "Received: from user-pc ([198.51.100.25])\r\n"
            "        by mail-pj1-f41.google.com with ESMTPSA id y789pjb.2;\r\n"
            "        Thu, 10 Sep 2026 09:59:58 -0700\r\n"
            "From: Alice Developer <alice@sih.gov.in>\r\n"
            "To: Recipient <recipient@sih.gov.in>\r\n"
            "Return-Path: <alice@sih.gov.in>\r\n"
            "Message-ID: <123456789.legit@sih.gov.in>\r\n"
            "Date: Thu, 10 Sep 2026 09:59:58 -0700\r\n"
            "Subject: SIH 2026 Security Update\r\n"
            "Authentication-Results: mx.google.com; spf=pass (google.com: domain of alice@sih.gov.in designates 209.85.216.41 as permitted sender) smtp.mailfrom=alice@sih.gov.in; dkim=pass header.i=@sih.gov.in\r\n"
            "DKIM-Signature: v=1; a=rsa-sha256; d=sih.gov.in; s=2026;\r\n\r\n"
            "Hello, this is a legitimate project update for SIH 2026."
        )

        header_res = self.header_forensics.analyze(sample_legit_email)
        auth_res = self.auth_analyzer.analyze(sample_legit_email)
        policy_res = self.policy_engine.evaluate(header_res, auth_res)

        self.assertEqual(header_res.originating_ip, "198.51.100.25")
        self.assertFalse(header_res.is_spoofed_domain)
        self.assertFalse(header_res.domain_mismatch)

        self.assertEqual(auth_res.spf_status, AuthStatus.PASS)
        self.assertEqual(auth_res.dkim_status, AuthStatus.PASS)
        self.assertTrue(auth_res.is_authenticated)

        self.assertEqual(policy_res.risk_level, RiskLevel.SAFE)
        self.assertEqual(policy_res.delivery_action, DeliveryAction.DELIVER)
        self.assertFalse(policy_res.is_quarantined)

    def test_spoofed_bec_email(self):
        sample_bec_email = (
            "Received: from malicious-node.evil.org ([198.51.100.99])\r\n"
            "        by ingress.mailtrace.internal with ESMTP id bec999;\r\n"
            "        Thu, 10 Sep 2026 10:15:00 -0700\r\n"
            "From: AICTE Director <accounts@aicte-gov-portal.co>\r\n"
            "Return-Path: <attacker@evil-phish.net>\r\n"
            "Reply-To: badguy@dropzone.com\r\n"
            "Message-ID: <invalid-id-format>\r\n"
            "Subject: URGENT: Institutional Fund Transfer Approval\r\n"
            "Authentication-Results: ingress.mailtrace.internal; spf=fail identity=mailfrom; dkim=fail\r\n\r\n"
            "Please wire transfer funds immediately."
        )

        header_res = self.header_forensics.analyze(sample_bec_email)
        auth_res = self.auth_analyzer.analyze(sample_bec_email)
        policy_res = self.policy_engine.evaluate(header_res, auth_res)

        self.assertTrue(header_res.is_spoofed_domain)
        self.assertTrue(header_res.domain_mismatch)
        self.assertEqual(auth_res.spf_status, AuthStatus.FAIL)
        self.assertEqual(auth_res.dkim_status, AuthStatus.FAIL)

        self.assertEqual(policy_res.risk_level, RiskLevel.MALICIOUS)
        self.assertEqual(policy_res.delivery_action, DeliveryAction.QUARANTINE)
        self.assertTrue(policy_res.is_quarantined)

    def test_evidence_preservation_iso27037(self):
        raw_content = b"Sample email raw byte stream for evidence hashing."
        headers = {"From": "alice@example.com", "Subject": "Test"}

        dossier = self.evidence_preserver.preserve_evidence(
            raw_bytes=raw_content,
            headers=headers,
            sender="alice@example.com",
            recipient="bob@example.com",
        )

        self.assertTrue(dossier.iso_27037_compliant)
        self.assertTrue(dossier.bsa_admissible)
        self.assertEqual(len(dossier.raw_sha256), 64)
        self.assertTrue(self.evidence_preserver.verify_integrity(dossier, raw_content))

    def test_pii_redaction_and_aes256(self):
        sensitive_text = (
            "User details: Aadhaar 4532 9812 7643 and PAN ABCDE1234F. "
            "Contact: +919876543210."
        )

        redaction_res = self.pii_redactor.redact(sensitive_text)
        self.assertTrue(redaction_res.is_pii_present)
        self.assertIn("AADHAAR", redaction_res.pii_types_found)
        self.assertIn("PAN", redaction_res.pii_types_found)
        self.assertNotIn("4532 9812 7643", redaction_res.redacted_text)
        self.assertIn("[REDACTED-AADHAAR]", redaction_res.redacted_text)
        self.assertIn("[REDACTED-PAN]", redaction_res.redacted_text)

        # Test AES-256 Encryption / Decryption Roundtrip
        key = b"supersecretkeyforaes256testing123!"
        encrypted = self.pii_redactor.encrypt_aes256_gcm(sensitive_text, key)
        decrypted = self.pii_redactor.decrypt_aes256_gcm(encrypted, key)
        self.assertEqual(decrypted, sensitive_text)

    def test_unknown_authentication_state(self):
        sample_no_auth_email = (
            "From: user@unknown-domain.org\r\n"
            "Subject: Hello\r\n\r\n"
            "Simple text."
        )

        auth_res = self.auth_analyzer.analyze(sample_no_auth_email)
        self.assertEqual(auth_res.spf_status, AuthStatus.UNKNOWN)
        self.assertEqual(auth_res.dkim_status, AuthStatus.NONE)

    def test_url_phishing_analysis(self):
        from backend.analysis.url_analysis import URLAnalyzer
        url_analyzer = URLAnalyzer()
        phishing_text = "Please log in immediately at http://198.51.100.99/login and http://login-nic.gov-portal.co/verify"
        res = url_analyzer.analyze(phishing_text)

        self.assertTrue(res.has_phishing_links)
        self.assertGreater(res.malicious_urls_count, 0)
        self.assertEqual(res.total_urls, 2)

    def test_attachment_inspection(self):
        from backend.analysis.attachment_analysis import AttachmentAnalyzer
        att_analyzer = AttachmentAnalyzer()
        attachments = [{"filename": "invoice_doc.pdf.exe", "mime_type": "application/x-msdownload", "size_bytes": 100000}]
        res = att_analyzer.analyze(attachments)

        self.assertTrue(res.has_dangerous_attachments)
        self.assertEqual(res.malicious_attachments_count, 1)

    def test_nlp_bec_detection(self):
        from backend.analysis.detection import NLPThreatDetector
        nlp_detector = NLPThreatDetector()
        res = nlp_detector.analyze(
            subject="URGENT: Mandated Institutional Fund Wire Transfer",
            body="Immediate wire transfer of funds to AICTE Director account within 2 hours.",
            sender_display_name="AICTE Director <director@aicte-gov-portal.co>"
        )

        self.assertTrue(res.is_executive_impersonation)
        self.assertTrue(res.is_payment_diversion)
        self.assertEqual(res.threat_category, "BEC_PAYMENT_DIVERSION")


if __name__ == "__main__":
    unittest.main()
