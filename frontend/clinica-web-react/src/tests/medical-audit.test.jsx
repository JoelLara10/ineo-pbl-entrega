// @vitest-environment jsdom
import React from 'react';
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import MedicalNote from '../pages/medico/MedicalNoteScreen';
import Prescription from '../pages/medico/PrescriptionScreen';
import Vitals from '../pages/medico/VitalSignsScreen';
import Diagnosis from '../pages/medico/DiagnosisScreen';
import Lab from '../pages/medico/LabExamsScreen';
import Imaging from '../pages/medico/ImagingExamsScreen';
import api from '../services/api';
import { clearClinicalCache } from '../services/clinicalCache';

vi.mock('../services/api', () => ({default:{get:vi.fn(), post:vi.fn()}}));
vi.mock('react-i18next', () => ({useTranslation:()=>({t:key=>key, i18n:{language:'es'}})}));
const patient = vi.hoisted(()=>({current:{id_atencion:1,Id_exp:1}}));
vi.mock('../context/PatientContext',()=>({usePatient:()=>({selectedPatient:patient.current})}));
beforeEach(()=>{vi.clearAllMocks();clearClinicalCache();patient.current={id_atencion:1,Id_exp:1};api.get.mockResolvedValue({data:[]});vi.spyOn(window,'alert').mockImplementation(()=>{});});
afterEach(()=>{cleanup();vi.restoreAllMocks();});
const forms=[['notes',MedicalNote],['prescription',Prescription],['vitals',Vitals],['diagnosis',Diagnosis],['lab',Lab],['imaging',Imaging]];
function show(Form){return render(<MemoryRouter><Form /></MemoryRouter>);}
describe.each(forms)('%s safety',(_name,Form)=>{
 it('shows a safe load failure and recovers on refresh',async()=>{
  api.get.mockRejectedValue(new Error('private mongodb password token'));
  show(Form);
  await waitFor(()=>expect(screen.getByRole('alert').textContent).toMatch(/conexión/));
  expect(document.body.textContent).not.toMatch(/private mongodb|password token/);
  api.get.mockImplementation(url=>Promise.resolve({data:url.endsWith('/diagnosis')?{}:[]}));
  const buttons=screen.getAllByRole('button');
  // Header has Back followed by Refresh in each medical form.
  fireEvent.click(buttons[1]);
  await waitFor(()=>expect(screen.queryByRole('alert')).toBeNull());
 });
 it('rejects an empty form without posting',async()=>{
  show(Form);
  await waitFor(()=>expect(api.get).toHaveBeenCalled());
  const save=screen.getAllByRole('button').find(button=>/\.save$|\.request$|\.update$/.test(button.textContent));
  expect(save).toBeTruthy(); fireEvent.click(save);
  expect(api.post).not.toHaveBeenCalled();
 });
});
it('preserves the note draft on failure and blocks concurrent submits',async()=>{
 show(MedicalNote);
 await waitFor(()=>expect(api.get).toHaveBeenCalled());
 fireEvent.change(screen.getAllByRole('textbox')[0],{target:{value:'QA SINTETICO'}});
 let reject;
 api.post.mockImplementation(()=>new Promise((_resolve,fail)=>{reject=fail;}));
 const save=screen.getByText('medicalSoap.save').closest('button');
 fireEvent.click(save);fireEvent.click(save);
 expect(api.post).toHaveBeenCalledTimes(1);
 reject(new Error('secret password'));
 await waitFor(()=>expect(window.alert).toHaveBeenCalled());
 expect(screen.getAllByRole('textbox')[0].value).toBe('QA SINTETICO');
});
it('rejects a partial prescription instead of dropping rows',async()=>{
 show(Prescription);
 fireEvent.change(screen.getAllByRole('textbox')[0],{target:{value:'QA NO ADMINISTRAR'}});
 fireEvent.click(screen.getByText('prescription.save').closest('button'));
 expect(api.post).not.toHaveBeenCalled();
});
it('rejects malformed vital numbers before posting',async()=>{
 show(Vitals);
 const fc=screen.getByPlaceholderText('lpm');
 fireEvent.change(fc,{target:{value:'72abc'}});
 fireEvent.click(screen.getByText('vitalSigns.save').closest('button'));
 expect(api.post).not.toHaveBeenCalled();
});
it('clears unsaved data when changing the selected patient',async()=>{
 const view=show(MedicalNote);
 fireEvent.change(screen.getAllByRole('textbox')[0],{target:{value:'PATIENT ONE DRAFT'}});
 patient.current={id_atencion:3,Id_exp:3};
 view.rerender(<MemoryRouter><MedicalNote /></MemoryRouter>);
 expect(screen.getAllByRole('textbox')[0].value).toBe('');
});
