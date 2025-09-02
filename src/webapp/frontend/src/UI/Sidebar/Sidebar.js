import React from 'react';
import styles from './Sidebar.module.css';
import Tooltip from '../Tooltip/Tooltip';

function Sidebar({ reportType, setReportType, releaseVersion, setReleaseVersion, selectedTeam, setSelectedTeam, teams, selectedStatuses, setSelectedStatuses, priorities, selectedPriorities, setSelectedPriorities, severities, selectedSeverities, setSelectedSeverities, platforms, selectedPlatforms, setSelectedPlatforms, emailRecipients, setEmailRecipients, includeAssigneesInEmail, setIncludeAssigneesInEmail, includeReporteesInEmail, setIncludeReporteesInEmail, releases, reportTypes, generateReport, loading, sendEmailReport, setSendEmailReport, includeAppLeadership, setIncludeAppLeadership, includeRegressionTeam, setIncludeRegressionTeam, includeTechLeads, setIncludeTechLeads, includeScrumMasters, setIncludeScrumMasters, includeAllAppTeams, setIncludeAllAppTeams, sendPerTeamEmails, setSendPerTeamEmails, isStatusDropdownOpen, setIsStatusDropdownOpen, isPlatformDropdownOpen, setIsPlatformDropdownOpen, isPriorityDropdownOpen, setIsPriorityDropdownOpen, isSeverityDropdownOpen, setIsSeverityDropdownOpen, showReportFilters, setShowReportFilters, showEmailSettings, setShowEmailSettings, emailGroups }) {

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

  const handlePriorityChange = (priority) => {
    if (priority === 'All') {
      setSelectedPriorities([]);
    } else {
      const newPriorities = selectedPriorities.includes(priority)
        ? selectedPriorities.filter(p => p !== priority)
        : [...selectedPriorities, priority];
      setSelectedPriorities(newPriorities);
    }
  };

  const handleSeverityChange = (severity) => {
    if (severity === 'All') {
      setSelectedSeverities([]);
    } else {
      const newSeverities = selectedSeverities.includes(severity)
        ? selectedSeverities.filter(s => s !== severity)
        : [...selectedSeverities, severity];
      setSelectedSeverities(newSeverities);
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
          <button
            className="btn btn-link p-0"
            type="button"
            onClick={() => setShowReportFilters(!showReportFilters)}
          >
            {showReportFilters ? 'Hide Report Filters' : 'Show Report Filters'}
          </button>
        </div>

        {showReportFilters && (
          <>
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
              <label className={styles.formLabel}>Priority</label>
              <div className={styles.statusDropdown}>
                <div className={styles.statusDropdownHeader} onClick={() => setIsPriorityDropdownOpen(!isPriorityDropdownOpen)}>
                  {selectedPriorities.length === 0 ? 'All' : selectedPriorities.join(', ')}
                  <span className={`${styles.dropdownArrow} ${isPriorityDropdownOpen ? styles.open : ''}`}>&#9662;</span>
                </div>
                {isPriorityDropdownOpen && (
                  <div className={styles.statusCheckboxes}>
                    <div key="all-priorities" className="form-check">
                      <input
                        type="checkbox"
                        className="form-check-input"
                        id="priority-all"
                        checked={selectedPriorities.length === 0}
                        onChange={() => handlePriorityChange('All')}
                      />
                      <label className="form-check-label" htmlFor="priority-all">
                        All
                      </label>
                    </div>
                    {priorities.slice(1).map(priority => (
                      <div key={priority} className="form-check">
                        <input
                          type="checkbox"
                          className="form-check-input"
                          id={`priority-${priority}`}
                          checked={selectedPriorities.includes(priority)}
                          onChange={() => handlePriorityChange(priority)}
                        />
                        <label className="form-check-label" htmlFor={`priority-${priority}`}>
                          {priority}
                        </label>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

            <div className="mb-3">
              <label className={styles.formLabel}>Severity</label>
              <div className={styles.statusDropdown}>
                <div className={styles.statusDropdownHeader} onClick={() => setIsSeverityDropdownOpen(!isSeverityDropdownOpen)}>
                  {selectedSeverities.length === 0 ? 'All' : selectedSeverities.join(', ')}
                  <span className={`${styles.dropdownArrow} ${isSeverityDropdownOpen ? styles.open : ''}`}>&#9662;</span>
                </div>
                {isSeverityDropdownOpen && (
                  <div className={styles.statusCheckboxes}>
                    <div key="all-severities" className="form-check">
                      <input
                        type="checkbox"
                        className="form-check-input"
                        id="severity-all"
                        checked={selectedSeverities.length === 0}
                        onChange={() => handleSeverityChange('All')}
                      />
                      <label className="form-check-label" htmlFor="severity-all">
                        All
                      </label>
                    </div>
                    {severities.slice(1).map(severity => (
                      <div key={severity} className="form-check">
                        <input
                          type="checkbox"
                          className="form-check-input"
                          id={`severity-${severity}`}
                          checked={selectedSeverities.includes(severity)}
                          onChange={() => handleSeverityChange(severity)}
                        />
                        <label className="form-check-label" htmlFor={`severity-${severity}`}>
                          {severity}
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
          </>
        )}

        <div className="mb-3">
          <button
            className="btn btn-link p-0"
            type="button"
            onClick={() => setShowEmailSettings(!showEmailSettings)}
          >
            {showEmailSettings ? 'Hide Email Notification Settings' : 'Show Email Notification Settings'}
          </button>
        </div>

        {showEmailSettings && (
          <div className={styles.emailOptionsContainer}>
            <div className={styles.emailSection}>
              <h6 className={styles.emailSectionHeader}>Direct Recipients</h6>
              {emailRecipients.map((email, index) => (
                <div key={index} className="input-group mb-2">
                  <input
                    type="email"
                    className="form-control"
                    placeholder="Enter email address..."
                    value={email}
                    onChange={(e) => handleEmailChange(index, e.target.value)}
                  />
                  {emailRecipients.length > 1 && (
                    <button
                      className="btn btn-outline-danger"
                      type="button"
                      onClick={() => removeEmailInput(index)}
                    >
                      -
                    </button>
                  )}
                </div>
              ))}
              <button
                className="btn btn-outline-primary"
                type="button"
                onClick={addEmailInput}
              >
                + Add another email
              </button>
            </div>

            <div className={styles.emailSection}>
              <h6 className={styles.emailSectionHeader}>Recipient Groups</h6>
              <div className="mb-3">
                <label className="form-label">Send a copy to:</label>
                <div className="mb-3 form-check">
                  <input
                    type="checkbox"
                    className="form-check-input"
                    id="sendPerTeamEmails"
                    checked={sendPerTeamEmails}
                    onChange={(e) => setSendPerTeamEmails(e.target.checked)}
                  />
                  <label className="form-check-label" htmlFor="sendPerTeamEmails">
                    Individual Teams
                  </label>
                                    <Tooltip text={`Sends a separate email to each team with only their issues. Emails: ${emailGroups.team_email_distros ? Object.values(emailGroups.team_email_distros).join(', ') : ''}`}><span className={styles.infoIcon}>?</span></Tooltip>
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
                    App Leadership
                  </label>
                                    <Tooltip text={`Sends a copy of the report to the App Leadership group. Emails: ${emailGroups.app_leadership ? emailGroups.app_leadership.join(', ') : ''}`}><span className={styles.infoIcon}>?</span></Tooltip>
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
                    Regression Team
                  </label>
                                    <Tooltip text={`Sends a copy of the report to the Regression Team. Emails: ${emailGroups.regression_team ? emailGroups.regression_team.join(', ') : ''}`}><span className={styles.infoIcon}>?</span></Tooltip>
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
                    Tech Leads
                  </label>
                                    <Tooltip text={`Sends a copy of the report to the Tech Leads group. Emails: ${emailGroups.tech_leads ? emailGroups.tech_leads.join(', ') : ''}`}><span className={styles.infoIcon}>?</span></Tooltip>
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
                    Scrum Masters
                  </label>
                                    <Tooltip text={`Sends a copy of the report to the Scrum Masters group. Emails: ${emailGroups.scrum_masters ? emailGroups.scrum_masters.join(', ') : ''}`}><span className={styles.infoIcon}>?</span></Tooltip>
                </div>
                <div className="mb-3 form-check">
                  <input
                    type="checkbox"
                    className="form-check-input"
                    id="includeAllAppTeams"
                    checked={includeAllAppTeams}
                    onChange={(e) => setIncludeAllAppTeams(e.target.checked)}
                  />
                  <label className="form-check-label" htmlFor="includeAllAppTeams">
                    All APP Teams
                  </label>
                                    <Tooltip text={`Sends a copy of the report to all APP teams. Emails: ${emailGroups.all_app_teams ? emailGroups.all_app_teams.join(', ') : ''}`}><span className={styles.infoIcon}>?</span></Tooltip>
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
                    Assignees of issues in the report
                  </label>
                                    <Tooltip text="Includes the assignees of the issues in the report as recipients."><span className={styles.infoIcon}>?</span></Tooltip>
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
                    Reporters of issues in the report
                  </label>
                                    <Tooltip text="Includes the reporters of the issues in the report as recipients."><span className={styles.infoIcon}>?</span></Tooltip>
                </div>
              </div>
            </div>
          </div>
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