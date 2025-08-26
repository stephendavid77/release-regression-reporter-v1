import React from 'react';
import styles from './Sidebar.module.css';

function Sidebar({ reportType, setReportType, releaseVersion, setReleaseVersion, emailRecipients, setEmailRecipients, includeAssigneesInEmail, setIncludeAssigneesInEmail, includeReporteesInEmail, setIncludeReporteesInEmail, releases, reportTypes, generateReport, loading, sendEmailReport, setSendEmailReport, includeAppLeadership, setIncludeAppLeadership, includeRegressionTeam, setIncludeRegressionTeam, includeTechLeads, setIncludeTechLeads, includeScrumMasters, setIncludeScrumMasters }) {

  const handleEmailChange = (index, value) => {
    const newEmails = [...emailRecipients];
    newEmails[index] = value;
    setEmailRecipients(newEmails);
  };

  const addEmailInput = () => {
    setEmailRecipients([...emailRecipients, '']);
  };

  const removeEmailInput = (index) => {
    const newEmails = [...emailRecipients];
    newEmails.splice(index, 1);
    setEmailRecipients(newEmails);
  };

  return (
    <div className={styles.sidebar}>
      <div className={styles.sidebarHeader}>
        <h2>APP Regression - Insight Hub</h2>
      </div>
      <div className={styles.sidebarContent}>
        <div className="mb-3">
          <label htmlFor="reportType" className={styles.formLabel}>Report Type</label>
          <select
            id="reportType"
            className="form-select"
            value={reportType}
            onChange={(e) => setReportType(e.target.value)}
          >
            {reportTypes.map(rt => (
              <option key={rt.name} value={rt.name}>{rt.name}</option>
            ))}
          </select>
          <div className={styles.formText}>
            {reportTypes.find(rt => rt.name === reportType)?.description}
          </div>
        </div>

        <div className="mb-3">
          <label htmlFor="releaseVersion" className={styles.formLabel}>Release Version</label>
          <select
            id="releaseVersion"
            className="form-select"
            value={releaseVersion}
            onChange={(e) => setReleaseVersion(e.target.value)}
          >
            {releases.map(r => (
              <option key={r} value={r}>{r}</option>
            ))}
          </select>
        </div>

        <div className="mb-3 form-check">
          <input
            type="checkbox"
            className="form-check-input"
            id="sendEmailReport"
            checked={sendEmailReport}
            onChange={(e) => setSendEmailReport(e.target.checked)}
          />
          <label className="form-check-label" htmlFor="sendEmailReport">
            Send Email Report
          </label>
        </div>

        {sendEmailReport && (
          <>
            <div className="mb-3">
              <label className="form-label">Email Recipients</label>
              <div className={styles.formText}>
                Enter email addresses manually, or select from the options below.
              </div>
              {emailRecipients.map((email, index) => (
                <div key={index} className="input-group mb-2">
                  <input
                    type="email"
                    className="form-control"
                    placeholder="Enter email"
                    value={email}
                    onChange={(e) => handleEmailChange(index, e.target.value)}
                  />
                  <button
                    className="btn btn-outline-danger"
                    type="button"
                    onClick={() => removeEmailInput(index)}
                  >
                    -
                  </button>
                </div>
              ))}
              <button
                className="btn btn-outline-primary"
                type="button"
                onClick={addEmailInput}
              >
                + Add Email
              </button>
            </div>

            <div className="mb-3 form-check">
              <input
                type="checkbox"
                className="form-check-input"
                id="includeAssigneesInEmail"
                checked={includeAssigneesInEmail}
                onChange={(e) => setIncludeAssigneesInEmail(e.target.checked)}
              />
              <label className="form-check-label" htmlFor="includeAssigneesInEmail">
                Include Assignees in Email Report
              </label>
            </div>

            <div className="mb-3 form-check">
              <input
                type="checkbox"
                className="form-check-input"
                id="includeReporteesInEmail"
                checked={includeReporteesInEmail}
                onChange={(e) => setIncludeReporteesInEmail(e.target.checked)}
              />
              <label className="form-check-label" htmlFor="includeReporteesInEmail">
                Include Reportees in Email Report
              </label>
            </div>

            <div className="mb-3 form-check">
              <input
                type="checkbox"
                className="form-check-input"
                id="includeAppLeadership"
                checked={includeAppLeadership}
                onChange={(e) => setIncludeAppLeadership(e.target.checked)}
              />
              <label className="form-check-label" htmlFor="includeAppLeadership">
                Include App Leadership
              </label>
            </div>

            <div className="mb-3 form-check">
              <input
                type="checkbox"
                className="form-check-input"
                id="includeRegressionTeam"
                checked={includeRegressionTeam}
                onChange={(e) => setIncludeRegressionTeam(e.target.checked)}
              />
              <label className="form-check-label" htmlFor="includeRegressionTeam">
                Include Regression Team
              </label>
            </div>

            <div className="mb-3 form-check">
              <input
                type="checkbox"
                className="form-check-input"
                id="includeTechLeads"
                checked={includeTechLeads}
                onChange={(e) => setIncludeTechLeads(e.target.checked)}
              />
              <label className="form-check-label" htmlFor="includeTechLeads">
                Include Tech Leads
              </label>
            </div>

            <div className="mb-3 form-check">
              <input
                type="checkbox"
                className="form-check-input"
                id="includeScrumMasters"
                checked={includeScrumMasters}
                onChange={(e) => setIncludeScrumMasters(e.target.checked)}
              />
              <label className="form-check-label" htmlFor="includeScrumMasters">
                Include Scrum Masters
              </label>
            </div>
          </>
        )}

        <button
          className="btn btn-primary w-100"
          type="button"
          onClick={generateReport}
          disabled={loading}
        >
          {loading ? 'Generating...' : 'Generate Report'}
        </button>
      </div>
    </div>
  );
}

export default Sidebar;
