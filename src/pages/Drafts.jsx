import React, { useState, useEffect } from 'react';
import { FileText, Plus, Trash2, Edit3 } from 'lucide-react';
import { emailService } from '../services/emailService';
import { useLayoutContext } from '../components/layout/Layout';
import ComposeModal from '../components/common/ComposeModal';
import './Drafts.css';

export const Drafts = () => {
  const { searchQuery } = useLayoutContext() || {};
  const [drafts, setDrafts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isComposeOpen, setIsComposeOpen] = useState(false);

  useEffect(() => {
    const fetchDrafts = async () => {
      setLoading(true);
      const data = await emailService.getEmails('drafts');
      setDrafts(data);
      setLoading(false);
    };
    fetchDrafts();
  }, []);

  const filteredDrafts = drafts.filter((item) => {
    if (searchQuery && searchQuery.trim() !== '') {
      const q = searchQuery.toLowerCase();
      return (
        (item.recipient && item.recipient.toLowerCase().includes(q)) ||
        (item.subject && item.subject.toLowerCase().includes(q)) ||
        (item.preview && item.preview.toLowerCase().includes(q))
      );
    }
    return true;
  });

  return (
    <div className="drafts-page">
      <div className="page-header">
        <div className="header-title">
          <FileText size={22} className="text-cyan" />
          <h2>Saved Drafts</h2>
          <span className="count-badge">{filteredDrafts.length} Unsent Drafts</span>
        </div>

        <button className="btn-compose-trigger" onClick={() => setIsComposeOpen(true)}>
          <Plus size={16} />
          <span>+ Compose New</span>
        </button>
      </div>

      <div className="drafts-table-card">
        {loading ? (
          <div className="drafts-loading">Loading Saved Drafts...</div>
        ) : filteredDrafts.length === 0 ? (
          <div className="drafts-empty">
            <FileText size={40} className="text-muted" />
            <h3>No Unsent Drafts Found</h3>
            <p>No draft messages match your search query.</p>
            <button className="btn-compose-inline" onClick={() => setIsComposeOpen(true)}>
              <Plus size={16} />
              <span>Create Draft</span>
            </button>
          </div>
        ) : (
          <div className="email-rows-list">
            {filteredDrafts.map((draft) => (
              <div key={draft.id} className="draft-row">
                <div className="draft-recipient">
                  <span className="draft-tag">Draft</span>
                  <span className="recipient-name">To: {draft.recipient || '(No Recipient)'}</span>
                </div>

                <div className="draft-content">
                  <span className="draft-subject">{draft.subject || '(No Subject)'}</span>
                  <span className="draft-preview">— {draft.preview}</span>
                </div>

                <div className="draft-meta">
                  <span className="draft-time">{draft.date}</span>
                  <button className="btn-icon-action" title="Edit Draft" onClick={() => setIsComposeOpen(true)}>
                    <Edit3 size={15} />
                  </button>
                  <button className="btn-icon-action btn-delete" title="Discard Draft">
                    <Trash2 size={15} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <ComposeModal 
        isOpen={isComposeOpen}
        onClose={() => setIsComposeOpen(false)}
        onSend={async (emailData) => {
          await emailService.sendEmail(emailData);
        }}
      />
    </div>
  );
};

export default Drafts;
