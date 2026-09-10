import React, { useState } from 'react';
import { X, Send, Paperclip, Shield, CheckCircle } from 'lucide-react';
import './ComposeModal.css';

export const ComposeModal = ({ isOpen, onClose, onSend }) => {
  const [recipient, setRecipient] = useState('');
  const [subject, setSubject] = useState('');
  const [body, setBody] = useState('');
  const [file, setFile] = useState(null);
  const [isSending, setIsSending] = useState(false);
  const [sendSuccess, setSendSuccess] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!recipient || !subject) return;

    setIsSending(true);
    await onSend({ recipient, subject, body, attachment: file });
    setIsSending(false);
    setSendSuccess(true);

    setTimeout(() => {
      setSendSuccess(false);
      setRecipient('');
      setSubject('');
      setBody('');
      setFile(null);
      onClose();
    }, 1200);
  };

  return (
    <div className="modal-backdrop">
      <div className="compose-modal-card">
        {/* Modal Header */}
        <div className="compose-header">
          <div className="compose-title">
            <Shield size={18} className="text-cyan" />
            <span>Compose Message — MailTrace Gateway Outbound</span>
          </div>
          <button className="btn-close-modal" onClick={onClose}>
            <X size={18} />
          </button>
        </div>

        {sendSuccess ? (
          <div className="compose-success-view">
            <CheckCircle size={48} className="text-emerald" />
            <h3>Pre-Delivery Check Passed</h3>
            <p>Outbound message signed and queued for delivery</p>
          </div>
        ) : (
          /* Compose Form */
          <form onSubmit={handleSubmit} className="compose-form">
            <div className="form-group">
              <label>To:</label>
              <input 
                type="email" 
                placeholder="recipient@domain.com"
                value={recipient}
                onChange={(e) => setRecipient(e.target.value)}
                required
              />
            </div>

            <div className="form-group">
              <label>Subject:</label>
              <input 
                type="text" 
                placeholder="Message Subject..."
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
                required
              />
            </div>

            <div className="form-group flex-1">
              <textarea 
                placeholder="Type your message content here..."
                value={body}
                onChange={(e) => setBody(e.target.value)}
                rows={8}
              />
            </div>

            {/* File Attachment preview */}
            {file && (
              <div className="attachment-chip">
                <Paperclip size={14} />
                <span>{file.name} ({Math.round(file.size / 1024)} KB)</span>
                <button type="button" onClick={() => setFile(null)} className="btn-remove-file">
                  <X size={12} />
                </button>
              </div>
            )}

            {/* Modal Footer Controls */}
            <div className="compose-footer">
              <div className="footer-left">
                <label className="btn-attach-file">
                  <Paperclip size={16} />
                  <span>Attach File</span>
                  <input 
                    type="file" 
                    onChange={(e) => setFile(e.target.files[0])} 
                    hidden 
                  />
                </label>
                <span className="footer-security-note">
                  🛡️ MailTrace outbound DKIM & SPF auto-signed
                </span>
              </div>

              <div className="footer-right">
                <button type="button" className="btn-cancel" onClick={onClose}>
                  Cancel
                </button>
                <button type="submit" className="btn-send-mail" disabled={isSending}>
                  {isSending ? (
                    <span>Scanning & Sending...</span>
                  ) : (
                    <>
                      <Send size={16} />
                      <span>Send Message</span>
                    </>
                  )}
                </button>
              </div>
            </div>
          </form>
        )}
      </div>
    </div>
  );
};

export default ComposeModal;
