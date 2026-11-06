"""Build a parameterized JMeter plan; no tokens are stored in report files."""
from pathlib import Path
import xml.etree.ElementTree as E


def prop(parent, tag, name, value):
    node = E.SubElement(parent, tag, name=name)
    node.text = str(value)
    return node


def component(parent, tag, name, **attrs):
    node = E.SubElement(parent, tag, guiclass=attrs.pop('gui', tag + 'Gui'),
                        testclass=tag, testname=name, enabled='true', **attrs)
    tree = E.SubElement(parent, 'hashTree')
    return node, tree


root = E.Element('jmeterTestPlan', version='1.2', properties='5.0', jmeter='5.6.3')
tree = E.SubElement(root, 'hashTree')
plan, pt = component(tree, 'TestPlan', 'API QA real', gui='TestPlanGui')
prop(plan, 'boolProp', 'TestPlan.functional_mode', 'false')
arguments = E.SubElement(plan, 'elementProp', name='TestPlan.user_defined_variables',
                         elementType='Arguments', guiclass='ArgumentsPanel', testclass='Arguments')
E.SubElement(arguments, 'collectionProp', name='Arguments.arguments')
group, gt = component(pt, 'ThreadGroup', 'Usuarios autenticados', gui='ThreadGroupGui')
prop(group, 'stringProp', 'ThreadGroup.on_sample_error', 'continue')
loop = E.SubElement(group, 'elementProp', name='ThreadGroup.main_controller', elementType='LoopController')
prop(loop, 'boolProp', 'LoopController.continue_forever', 'false')
prop(loop, 'stringProp', 'LoopController.loops', '${__P(loops,-1)}')
for key, value in [('num_threads', '${__P(users,1)}'), ('ramp_time', '${__P(ramp,1)}'),
                   ('duration', '${__P(duration,60)}')]:
    prop(group, 'stringProp', 'ThreadGroup.' + key, value)
prop(group, 'boolProp', 'ThreadGroup.scheduler', 'true')
headers, _ = component(gt, 'HeaderManager', 'JSON y sesión sintética', gui='HeaderPanel')
collection = E.SubElement(headers, 'collectionProp', name='HeaderManager.headers')
for name, value in [('Content-Type', 'application/json'), ('Authorization', 'Bearer ${token}')]:
    element = E.SubElement(collection, 'elementProp', name='', elementType='Header')
    prop(element, 'stringProp', 'Header.name', name)
    prop(element, 'stringProp', 'Header.value', value)
timer, _ = component(gt, 'ConstantTimer', 'Pausa entre solicitudes', gui='ConstantTimerGui')
prop(timer, 'stringProp', 'ConstantTimer.delay', '${__P(pause,1000)}')


def sampler(parent, name, path, method='GET', payload=None, checks=''):
    node, children = component(parent, 'HTTPSamplerProxy', name, gui='HttpTestSampleGui')
    args = E.SubElement(node, 'elementProp', name='HTTPsampler.Arguments', elementType='Arguments')
    entries = E.SubElement(args, 'collectionProp', name='Arguments.arguments')
    if payload:
        arg = E.SubElement(entries, 'elementProp', name='', elementType='HTTPArgument')
        prop(arg, 'boolProp', 'HTTPArgument.always_encode', 'false')
        prop(arg, 'stringProp', 'Argument.value', payload)
        prop(arg, 'stringProp', 'Argument.metadata', '=')
        prop(node, 'boolProp', 'HTTPSampler.postBodyRaw', 'true')
    for key,value in [('domain','127.0.0.1'),('port','5029'),('protocol','http'),
                      ('path',path),('method',method),('connect_timeout','10000'),('response_timeout','20000')]:
        prop(node,'stringProp','HTTPSampler.'+key,value)
    prop(node,'boolProp','HTTPSampler.use_keepalive','true')
    assertion, _ = component(children, 'JSR223Assertion', 'HTTP y contrato JSON', gui='TestBeanGUI')
    prop(assertion,'stringProp','scriptLanguage','groovy')
    prop(assertion,'stringProp','cacheKey','true')
    prop(assertion,'stringProp','script', '''import groovy.json.JsonSlurper
try {
  assert prev.getResponseCode() == '200'
  def data = new JsonSlurper().parseText(prev.getResponseDataAsString())
  assert data instanceof Map
  ''' + checks + '''
} catch (Throwable problem) {
  AssertionResult.setFailure(true)
  AssertionResult.setFailureMessage('HTTP/JSON contract assertion failed')
}''')
    return children


once, ot = component(gt, 'OnceOnlyController', 'Login por usuario', gui='OnceOnlyControllerGui')
login = sampler(ot, 'login', '/api/v1/auth/login', 'POST',
                '{"username":"${__env(INEO_QA_USERNAME)}","password":"${__env(INEO_QA_PASSWORD)}"}',
                "assert data.token instanceof String; assert data.token.length() > 20")
extractor, _ = component(login, 'JSONPostProcessor', 'Token en memoria', gui='JSONPostProcessorGui')
for key,value in [('referenceNames','token'),('jsonPathExprs','$.token'),('match_numbers','1'),('defaultValues','INVALID')]:
    prop(extractor,'stringProp','JSONPostProcessor.'+key,value)
sampler(gt,'patients','${__P(path,/api/v1/patients)}',checks='assert data.groups instanceof List; assert data.pagination instanceof Map')
sampler(gt,'studies','/api/v1/studies/counts')
sampler(gt,'analytics','/api/v1/analytics/dashboard')
sampler(gt,'spark_overview','/api/v1/spark/overview',checks="assert ['analytics','met','clinical','unsupervised'].every { data.containsKey(it) }")
E.indent(root)
E.ElementTree(root).write(Path(__file__).with_name('api.jmx'),encoding='utf-8',xml_declaration=True)
