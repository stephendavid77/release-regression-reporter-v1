import React, { useState, useEffect } from 'react';
import styles from './Loader.module.css';

// Fisher-Yates (Knuth) shuffle algorithm
const shuffleArray = (array) => {
  let currentIndex = array.length, randomIndex;

  // While there remain elements to shuffle.
  while (currentIndex !== 0) {
    // Pick a remaining element.
    randomIndex = Math.floor(Math.random() * currentIndex);
    currentIndex--;

    // And swap it with the current element.
    [array[currentIndex], array[randomIndex]] = [
      array[randomIndex], array[currentIndex]];
  }

  return array;
};

function Loader() {
  const [timer, setTimer] = useState(0);
  const [fact, setFact] = useState('');
  const [facts, setFacts] = useState(Array);
  const [factIndex, setFactIndex] = useState(0); // New state for current fact index

  useEffect(() => {
    const fetchFacts = async () => {
      try {
        console.log("Fetching interesting facts...");
        const response = await fetch('/interesting_facts.json');
        const data = await response.json();
        console.log("Facts data before shuffle:", data);
        const shuffledData = shuffleArray([...data]); // Shuffle a copy of the data
        console.log("Facts data after shuffle:", shuffledData);
        setFacts(shuffledData);
        setFact(shuffledData[0]); // Set initial fact
        setFactIndex(0); // Initialize index
      } catch (error) {
        console.error('Error fetching facts:', error);
      }
    };

    fetchFacts();
  }, []);

  useEffect(() => {
    const timerInterval = setInterval(() => {
      setTimer(prevTimer => prevTimer + 1);
    }, 1000);

    const factInterval = setInterval(() => {
      if (facts.length > 0) {
        setFactIndex(prevIndex => {
          let nextIndex = prevIndex + 1;
          if (nextIndex >= facts.length) {
            // Reshuffle and reset index if we reach the end
            setFacts(shuffleArray([...facts])); // Reshuffle a copy
            nextIndex = 0;
          }
          setFact(facts[nextIndex]);
          return nextIndex;
        });
      }
    }, 5000);

    return () => {
      clearInterval(timerInterval);
      clearInterval(factInterval);
    };
  }, [facts]); // Depend on facts to re-run when facts array is reshuffled

  return (
    <div className={styles.loadingOverlay}>
      <div className={styles.loaderContent}>
        <div className="spinner-border text-primary" style={{ width: '3rem', height: '3rem' }} role="status">
          <span className="sr-only">Loading...</span>
        </div>
        <h2>Processing request, please wait...</h2>
        <div className={styles.timerContainer}>
          Time Elapsed: <span id="time-elapsed">{new Date(timer * 1000).toISOString().substr(14, 5)}</span>
        </div>
        <div className={styles.factContainer}>
          <p>Did you know?</p>
          <p>{fact}</p>
        </div>
      </div>
    </div>
  );
}

export default Loader;
