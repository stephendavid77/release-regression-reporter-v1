import React, { useState, useEffect } from 'react';
import ReactDOM from 'react-dom';
import axios from 'axios';
import Sidebar from '../Sidebar/Sidebar';
import Report from '../Report/Report';
import Loader from '../Loader/Loader';
import MessageOverlay from '../MessageOverlay/MessageOverlay';
import styles from './App.module.css';

function App() {
  const [reportType, setReportType] = useState('All Issues');
  const [releaseVersion, setReleaseVersion] = useState('APP 25.08-R2');
  const [selectedTeam, setSelectedTeam] = useState('All');
  const [teams, setTeams] = useState([]);
  const [selectedStatuses, setSelectedStatuses] = useState([]);
  const [priorities, setPriorities] = useState([]);
  const [selectedPriorities, setSelectedPriorities] = useState([]);
  const [severities, setSeverities] = useState([]);
  const [selectedSeverities, setSelectedSeverities] = useState([]);
  const [platforms, setPlatforms] = useState([]);
  const [selectedPlatforms, setSelectedPlatforms] = useState([]);
  const [emailRecipients, setEmailRecipients] = useState(['']);
  const [includeAssigneesInEmail, setIncludeAssigneesInEmail] = useState(false);
  const [includeReporteesInEmail, setIncludeReporteesInEmail] = useState(false);
  const [releases, setReleases] = useState([]);
  const [reportTypes, setReportTypes] = useState([]);
  const [report, setReport] = useState('');
  const [loading, setLoading] = useState(false);
  
  const [includeAppLeadership, setIncludeAppLeadership] = useState(false);
  const [includeRegressionTeam, setIncludeRegressionTeam] = useState(false);
  const [includeTechLeads, setIncludeTechLeads] = useState(false);
  const [includeScrumMasters, setIncludeScrumMasters] = useState(false);
  const [includeAllAppTeams, setIncludeAllAppTeams] = useState(false);
  const [sendPerTeamEmails, setSendPerTeamEmails] = useState(false);
  const [showMessageOverlay, setShowMessageOverlay] = useState(false);
  const [overlayMessage, setOverlayMessage] = useState('');
  const [overlayMessageType, setOverlayMessageType] = useState('info');
  const [isStatusDropdownOpen, setIsStatusDropdownOpen] = useState(false);
  const [isPlatformDropdownOpen, setIsPlatformDropdownOpen] = useState(false);
  const [isPriorityDropdownOpen, setIsPriorityDropdownOpen] = useState(false);
  const [isSeverityDropdownOpen, setIsSeverityDropdownOpen] = useState(false);
  const [showReportFilters, setShowReportFilters] = useState(false);
  const [showEmailSettings, setShowEmailSettings] = useState(false);
  
  const [emailGroups, setEmailGroups] = useState({});

  useEffect(() => {
    // Fetch releases
    axios.get('/api/releases')
      .then(response => {
        setReleases(response.data.releases);
        if (response.data.releases.length > 0) {
          setReleaseVersion(response.data.releases[0]); // Set default to first release
        }
      })
      .catch(error => console.error('Error fetching releases:', error));

    // Fetch report types
    axios.get('/api/report-types')
      .then(response => {
        setReportTypes(response.data.report_types);
        if (response.data.report_types.length > 0) {
          setReportType(response.data.report_types[0].name); // Set default to first report type
        }
      })
      .catch(error => console.error('Error fetching report types:', error));

    // Fetch teams
    axios.get('/api/teams')
      .then(response => {
        setTeams(['All', ...response.data.teams]);
      })
      .catch(error => console.error('Error fetching teams:', error));

    // Fetch reports to extract platforms
    axios.get('/api/reports')
      .then(response => {
        const platformNames = response.data.reports;
        setPlatforms(['All', ...platformNames]);
      })
      .catch(error => console.error('Error fetching reports:', error));

    // Fetch priorities
    axios.get('/api/priorities')
      .then(response => {
        setPriorities(['All', ...response.data.priorities]);
      })
      .catch(error => console.error('Error fetching priorities:', error));

    // Fetch severities
    axios.get('/api/severities')
      .then(response => {
        setSeverities(['All', ...response.data.severities]);
      })
      .catch(error => console.error('Error fetching severities:', error));

    // Fetch email groups
    axios.get('/api/email-groups')
      .then(response => {
        setEmailGroups(response.data);
      })
      .catch(error => console.error('Error fetching email groups:', error));
  }, []);

  const generateReport = async () => {
    setLoading(true);
    setOverlayMessage(''); // Clear previous message
    setShowMessageOverlay(false); // Hide previous overlay
    setOverlayMessageType('info'); // Reset type
    try {
      const shouldSendEmail = emailRecipients.filter(email => email !== '').length > 0 ||
        includeAssigneesInEmail ||
        includeReporteesInEmail ||
        includeAppLeadership ||
        includeRegressionTeam ||
        includeTechLeads ||
        includeScrumMasters ||
        includeAllAppTeams ||
        sendPerTeamEmails;

      const response = await axios.post('/api/generate-report', {
        report_type: reportType,
        release_version: releaseVersion,
        selected_team: selectedTeam,
        selected_statuses: selectedStatuses,
        selected_priorities: selectedPriorities,
        selected_severities: selectedSeverities,
        selected_platforms: selectedPlatforms,
        send_email_report: shouldSendEmail,
        email_recipients: emailRecipients.filter(email => email !== ''),
        include_assignees_in_email_report: includeAssigneesInEmail,
        include_reportees_in_email_report: includeReporteesInEmail,
        include_app_leadership: includeAppLeadership,
        include_regression_team: includeRegressionTeam,
        include_tech_leads: includeTechLeads,
        include_scrum_masters: includeScrumMasters,
        include_all_app_teams: includeAllAppTeams,
        send_per_team_emails: sendPerTeamEmails,
      });
      setReport(response.data.report);

      if (shouldSendEmail) {
        setOverlayMessage('Your report has been successfully generated and emailed.');
      } else {
        setOverlayMessage('Your report has been successfully generated.');
      }
      setOverlayMessageType('success');
      setShowMessageOverlay(true);

    } catch (error) {
      console.error('Error generating report:', error);
      setReport('<p class="text-danger">Error generating report.</p>');
      setOverlayMessage('There was an issue generating your report. Please try again.');
      setOverlayMessageType('error');
      setShowMessageOverlay(true);
    }
    setLoading(false);
  };

  return (
    <div className={styles.appContainer}>
      <Sidebar
        reportType={reportType}
        setReportType={setReportType}
        releaseVersion={releaseVersion}
        setReleaseVersion={setReleaseVersion}
        selectedTeam={selectedTeam}
        setSelectedTeam={setSelectedTeam}
        teams={teams}
        selectedStatuses={selectedStatuses}
        setSelectedStatuses={setSelectedStatuses}
        priorities={priorities}
        selectedPriorities={selectedPriorities}
        setSelectedPriorities={setSelectedPriorities}
        severities={severities}
        selectedSeverities={selectedSeverities}
        setSelectedSeverities={setSelectedSeverities}
        platforms={platforms}
        selectedPlatforms={selectedPlatforms}
        setSelectedPlatforms={setSelectedPlatforms}
        emailRecipients={emailRecipients}
        setEmailRecipients={setEmailRecipients}
        includeAssigneesInEmail={includeAssigneesInEmail}
        setIncludeAssigneesInEmail={setIncludeAssigneesInEmail}
        includeReporteesInEmail={includeReporteesInEmail}
        setIncludeReporteesInEmail={setIncludeReporteesInEmail}
        releases={releases}
        reportTypes={reportTypes}
        generateReport={generateReport}
        loading={loading}
        
        includeAppLeadership={includeAppLeadership}
        setIncludeAppLeadership={setIncludeAppLeadership}
        includeRegressionTeam={includeRegressionTeam}
        setIncludeRegressionTeam={setIncludeRegressionTeam}
        includeTechLeads={includeTechLeads}
        setIncludeTechLeads={setIncludeTechLeads}
        includeScrumMasters={includeScrumMasters}
        setIncludeScrumMasters={setIncludeScrumMasters}
        includeAllAppTeams={includeAllAppTeams}
        setIncludeAllAppTeams={setIncludeAllAppTeams}
        sendPerTeamEmails={sendPerTeamEmails}
        setSendPerTeamEmails={setSendPerTeamEmails}
        isStatusDropdownOpen={isStatusDropdownOpen}
        setIsStatusDropdownOpen={setIsStatusDropdownOpen}
        isPlatformDropdownOpen={isPlatformDropdownOpen}
        setIsPlatformDropdownOpen={setIsPlatformDropdownOpen}
        isPriorityDropdownOpen={isPriorityDropdownOpen}
        setIsPriorityDropdownOpen={setIsPriorityDropdownOpen}
        isSeverityDropdownOpen={isSeverityDropdownOpen}
        setIsSeverityDropdownOpen={setIsSeverityDropdownOpen}
        showReportFilters={showReportFilters}
        setShowReportFilters={setShowReportFilters}
        showEmailSettings={showEmailSettings}
        setShowEmailSettings={setShowEmailSettings}
        
        emailGroups={emailGroups}
      />
      <Report report={report} />
      {loading && ReactDOM.createPortal(
        <Loader />,
        document.body
      )}
      {showMessageOverlay && (
        <MessageOverlay
          message={overlayMessage}
          type={overlayMessageType} // Pass new prop
          onClose={() => setShowMessageOverlay(false)}
        />
      )}
    </div>
  );
}

export default App;