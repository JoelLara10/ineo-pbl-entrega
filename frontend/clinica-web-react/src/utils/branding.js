// Replace only the former default; preserve names customized by the clinic.
export function currentClinicSettings(settings) {
  return settings?.nombreClinica === 'INEO Hospital'
    ? { ...settings, nombreClinica: 'OftalCore Hospital' }
    : settings;
}
