// src/context/PatientContext.js
import React, { createContext, useCallback, useEffect, useMemo, useState, useContext } from 'react';

const PatientContext = createContext();
const STORAGE_KEY = 'ineo_selected_patient';

const getInitialPatient = () => {
  if (typeof window === 'undefined') {
    return { id_atencion: null, Id_exp: null };
  }

  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) return { id_atencion: null, Id_exp: null };
    return JSON.parse(raw);
  } catch (error) {
    console.error('Error restoring selected patient:', error);
    return { id_atencion: null, Id_exp: null };
  }
};

export const usePatient = () => {
  const context = useContext(PatientContext);
  if (!context) {
    throw new Error('usePatient must be used within PatientProvider');
  }
  return context;
};

export const PatientProvider = ({ children }) => {
  const [selectedPatient, setSelectedPatient] = useState(getInitialPatient);

  useEffect(() => {
    if (typeof window === 'undefined') return;

    try {
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify(selectedPatient));
    } catch (error) {
      console.error('Error persisting selected patient:', error);
    }
  }, [selectedPatient]);

  const selectPatient = useCallback((patientData) => {
    setSelectedPatient({
      id_atencion: patientData?.id_atencion || patientData?.id,
      Id_exp: patientData?.Id_exp || patientData?.id_exp || patientData?.exp,
      ...patientData, // por si quieres guardar todo el objeto
    });
  }, []);

  const value = useMemo(() => ({
    selectedPatient,
    setSelectedPatient,
    selectPatient,
  }), [selectedPatient, selectPatient]);

  return (
    <PatientContext.Provider value={value}>
      {children}
    </PatientContext.Provider>
  );
};