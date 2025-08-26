import React from 'react';
import styles from './Report.module.css';

function Report({ report }) {
  return (
    <div className={styles.reportContainer}>
      <div className={styles.reportContent}>
        {report ? (
          <div dangerouslySetInnerHTML={{ __html: report }} />
        ) : (
          <div className={styles.noReport}>
            <h2>No report generated yet.</h2>
            <p>Use the sidebar to generate a new report.</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default Report;
