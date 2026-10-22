import SparkAnalysisScreen from './SparkAnalysisScreen';
import AnalysisDashboard from './AnalysisCharts';
export default function UnsupervisedAnalyticsScreen() { return <SparkAnalysisScreen type="unsupervised" ResultsComponent={AnalysisDashboard} />; }
