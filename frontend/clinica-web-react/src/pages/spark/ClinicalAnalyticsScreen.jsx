import ClinicalAnalyticsPanel from './ClinicalAnalyticsPanel';
import SparkAnalysisScreen from './SparkAnalysisScreen';

export default function ClinicalAnalyticsScreen() {
  return <SparkAnalysisScreen type="clinical" ResultsComponent={ClinicalAnalyticsPanel} />;
}
