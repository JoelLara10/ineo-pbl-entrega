import { expect, it } from 'vitest';
import { currentClinicSettings } from '../utils/branding';

it('updates the former default without changing connection or custom settings', () => {
  const old = { nombreClinica: 'INEO Hospital', apiHost: 'qa.example.test', apiPort: '443', telefono: '555' };
  expect(currentClinicSettings(old)).toEqual({ ...old, nombreClinica: 'OftalCore Hospital' });
  expect(old.nombreClinica).toBe('INEO Hospital');
  const custom = { ...old, nombreClinica: 'Clínica personalizada' };
  expect(currentClinicSettings(custom)).toBe(custom);
});
