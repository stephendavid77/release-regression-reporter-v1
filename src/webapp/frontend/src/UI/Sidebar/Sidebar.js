import React, { useState } from 'react';
import styles from './Sidebar.module.css';

function Sidebar({ reportType, setReportType, releaseVersion, setReleaseVersion, selectedTeam, setSelectedTeam, teams, selectedStatuses, setSelectedStatuses, platforms, selectedPlatforms, setSelectedPlatforms, emailRecipients, setEmailRecipients, includeAssigneesInEmail, setIncludeAssigneesInEmail, includeReporteesInEmail, setIncludeReporteesInEmail, releases, reportTypes, generateReport, loading, sendEmailReport, setSendEmailReport, includeAppLeadership, setIncludeAppLeadership, includeRegressionTeam, setIncludeRegressionTeam, includeTechLeads, setIncludeTechLeads, includeScrumMasters, setIncludeScrumMasters }) {

  const [isStatusDropdownOpen, setIsStatusDropdownOpen] = useState(false);
  const [isPlatformDropdownOpen, setIsPlatformDropdownOpen] = useState(false);

  const statusGroups = {
    'Yet to be picked up': [
      'Backlog',
      'Ready'
    ],
    'In Development': [
      'In development',
      'Code Review'
    ],
    'Testing': [
      'Ready to Test',
      'In Test'
    ],
    'Review pending': [
      'Review'
    ],
    'Closed': [
      'Done',
      'Canceled'
    ]
  };

  const handleStatusChange = (status) => {
    if (status === 'All Issues') {
      setSelectedStatuses([]);
    } else {
      const newStatuses = selectedStatuses.includes(status)
        ? selectedStatuses.filter(s => s !== status)
        : [...selectedStatuses, status];
      setSelectedStatuses(newStatuses);
    }
  };

  const handlePlatformChange = (platform) => {
    if (platform === 'All') {
      setSelectedPlatforms([]);
    } else {
      const newPlatforms = selectedPlatforms.includes(platform)
        ? selectedPlatforms.filter(p => p !== platform)
        : [...selectedPlatforms, platform];
      setSelectedPlatforms(newPlatforms);
    }
  };

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

        <div className="mb-3">
          <label htmlFor="team" className={styles.formLabel}>Team</label>
          <select
            id="team"
            className="form-select"
            value={selectedTeam}
            onChange={(e) => setSelectedTeam(e.target.value)}
          >
            {teams.map(t => (
              <option key={t} value={t}>{t}</option>
            ))}
          </select>
        </div>

        <div className="mb-3">
          <label className={styles.formLabel}>Platform</label>
          <div className={styles.statusDropdown}>
            <div className={styles.statusDropdownHeader} onClick={() => setIsPlatformDropdownOpen(!isPlatformDropdownOpen)}>
              {selectedPlatforms.length === 0 ? 'All' : selectedPlatforms.join(', ')}
              <span className={`${styles.dropdownArrow} ${isPlatformDropdownOpen ? styles.open : ''}`}>&#9662;</span>
            </div>
            {isPlatformDropdownOpen && (
              <div className={styles.statusCheckboxes}>
                <div key="all-platforms" className="form-check">
                  <input
                    type="checkbox"
                    className="form-check-input"
                    id="platform-all"
                    checked={selectedPlatforms.length === 0}
                    onChange={() => handlePlatformChange('All')}
                  />
                  <label className="form-check-label" htmlFor="platform-all">
                    All
                  </label>
                </div>
                {platforms.slice(1).map(platform => (
                  <div key={platform} className="form-check">
                    <input
                      type="checkbox"
                      className="form-check-input"
                      id={`platform-${platform}`}
                      checked={selectedPlatforms.includes(platform)}
                      onChange={() => handlePlatformChange(platform)}
                    />
                    <label className="form-check-label" htmlFor={`platform-${platform}`}>
                      {platform}
                    </label>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        <div className="mb-3">
          <label className={styles.formLabel}>Jira Status</label>
          <div className={styles.statusDropdown}>
            <div className={styles.statusDropdownHeader} onClick={() => setIsStatusDropdownOpen(!isStatusDropdownOpen)}>
              {selectedStatuses.length === 0 ? 'All Issues' : selectedStatuses.join(', ')}
              <span className={`${styles.dropdownArrow} ${isStatusDropdownOpen ? styles.open : ''}`}>&#9662;</span>
            </div>
            {isStatusDropdownOpen && (
              <div className={styles.statusCheckboxes}>
                <div key="all-issues" className="form-check">
                  <input
                    type="checkbox"
                    className="form-check-input"
                    id="status-all-issues"
                    checked={selectedStatuses.length === 0}
                    onChange={() => handleStatusChange('All Issues')}
                  />
                  <label className="form-check-label" htmlFor="status-all-issues">
                    All Issues
                  </label>
                </div>
                {Object.entries(statusGroups).map(([group, statuses]) => (
                  <div key={group}>
                    <hr />
                    <h6>{group}</h6>
                    {statuses.map(status => (
                      <div key={status} className="form-check">
                        <input
                          type="checkbox"
                          className="form-check-input"
                          id={`status-${status}`}
                          checked={selectedStatuses.includes(status)}
                          onChange={() => handleStatusChange(status)}
                        />
                        <label className="form-check-label" htmlFor={`status-${status}`}>
                          {status}
                        </label>
                      </div>
                    ))}
                  </div>
                ))}
              </div>
            )}
          </div>
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