import React, { useEffect } from 'react';
import ReactDOM from 'react-dom';
import styles from './MessageOverlay.module.css';

function MessageOverlay({ message, type, onClose }) {
  let icon = null;
  let title = '';
  let contentClass = styles.overlayContent;

  if (type === 'success') {
    icon = <span className={`${styles.statusIcon} ${styles.successIcon}`}>&#10004;</span>; // Checkmark
    title = 'Report Generated!';
    contentClass = `${styles.overlayContent} ${styles.success}`;
  } else if (type === 'error') {
    icon = <span className={`${styles.statusIcon} ${styles.errorIcon}`}>&#10006;</span>; // Cross
    title = 'Generation Failed';
    contentClass = `${styles.overlayContent} ${styles.error}`;
  }

  useEffect(() => {
    const timer = setTimeout(() => {
      onClose();
    }, 3000); // Disappear after 3 seconds

    return () => clearTimeout(timer); // Cleanup on unmount
  }, [onClose]); // Re-run if onClose changes

  return ReactDOM.createPortal(
    <div className={styles.overlayBackdrop}>
      <div className={contentClass}>
        {icon}
        {title && <h2>{title}</h2>}
        <p>{message}</p>
        <button className={styles.closeButton} onClick={onClose}>Close</button>
      </div>
    </div>,
    document.body
  );
}

export default MessageOverlay;