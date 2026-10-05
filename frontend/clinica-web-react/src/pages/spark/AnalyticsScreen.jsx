import SparkAnalysisScreen from './SparkAnalysisScreen';
import AnalyticsGeneralPanel from './AnalyticsGeneralPanel';

export default function AnalyticsScreen() {
  return <SparkAnalysisScreen type="analytics" ResultsComponent={AnalyticsGeneralPanel} />;
}
