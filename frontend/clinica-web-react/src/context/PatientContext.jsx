// src/context/PatientContext.js
import React, { createContext, useCallback, useEffect, useMemo, useState, useContext } from 'react';
import { useAuth } from './AuthContext';

const PatientContext = createContext();
const getInitialPatient = () => ({ id_atencion: null, Id_exp: null });

export const usePatient = () => {
  const context = useContext(PatientContext);
  if (!context) {
    throw new Error('usePatient must be used within PatientProvider');
  }
  return context;
};

export const PatientProvider = ({ children }) => {
  const { isAuthenticated, loading: authLoading } = useAuth();
  const [selectedPatient, setSelectedPatient] = useState(getInitialPatient);

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      setSelectedPatient({ id_atencion: null, Id_exp: null });
    }
  }, [authLoading, isAuthenticated]);

  const selectPatient = useCallback((patientData) => {
    setSelectedPatient({
      ...patientData,
      id_atencion: patientData?.id_atencion ?? patientData?.id,
      Id_exp: patientData?.Id_exp ?? patientData?.id_exp ?? patientData?.exp,
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