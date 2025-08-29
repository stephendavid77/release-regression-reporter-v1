import React, { useEffect, useRef } from 'react';
import styles from './Report.module.css';

function Report({ report }) {
  const reportRef = useRef(null);

  useEffect(() => {
    const handleClick = (event) => {
      const header = event.target.closest('h2, h3');
      if (header && reportRef.current.contains(header)) {
        const content = header.nextElementSibling;
        if (content && (content.tagName === 'TABLE' || content.tagName === 'P')) {
          content.classList.toggle(styles.collapsed);
          header.classList.toggle(styles.active);
        }
      }
    };

    if (reportRef.current) {
      const headers = reportRef.current.querySelectorAll('h2, h3');
      headers.forEach(header => {
        header.classList.add(styles.collapsible);
      });
      reportRef.current.addEventListener('click', handleClick);
    }

    return () => {
      if (reportRef.current) {
        // eslint-disable-next-line react-hooks/exhaustive-deps
        reportRef.current.removeEventListener('click', handleClick);
      }
    };
  }, [report]);

  return (
    <div className={styles.reportContainer}>
      <div className={styles.reportContent} ref={reportRef}>
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
