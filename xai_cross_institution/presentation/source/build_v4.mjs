import fs from 'node:fs/promises';
import path from 'node:path';
import {Presentation,PresentationFile} from '@oai/artifact-tool';
import {build} from './content_v4.mjs';
const ws=process.env.WORKSPACE_DIR;
const skill=process.env.PRESENTATION_SKILL_DIR;
if(!ws||!skill)throw Error('Set WORKSPACE_DIR and PRESENTATION_SKILL_DIR to the local workspace and installed presentation skill.');
const {finalizePresentation,applyPresentationChartFont}=await import(path.join(skill,'container_tools/artifact_tool_utils.mjs'));
const buildDir=process.env.BUILD_DIR||path.join(ws,'work/replication_32/deck');
const final=process.env.FINAL_PPTX||path.join(ws,'outputs/xai_cross_institution/presentation/XAI_Research_Results_v4.pptx');
const facts=JSON.parse(await fs.readFile(path.join(ws,'outputs/xai_replication_32/results/REPORT_FACTS.json'),'utf8'));
const p=build(Presentation.create({slideSize:{width:1280,height:720}}),facts);
for(const s of p.slides.items)for(const c of s.charts.items)applyPresentationChartFont(c,{fontFamily:'Arial'});
await fs.mkdir(buildDir,{recursive:true});
await (await PresentationFile.exportPptx(p)).save(path.join(buildDir,'candidate.pptx'));
for(let i=0;i<p.slides.items.length;i++){const b=await p.export({slide:p.slides.items[i],format:'png',scale:1});await fs.writeFile(path.join(buildDir,`slide-${i+1}.png`),new Uint8Array(await b.arrayBuffer()));}
const tables=[2,4,8,9,10,11,12,13,14,15];
const result=await finalizePresentation({workspaceDir:ws,candidatePath:path.join(buildDir,'candidate.pptx'),finalPath:final,pythonExecutable:process.env.RUNTIME_PYTHON,integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit',...tables.flatMap(n=>['--require-native-table-slide',String(n)])],requiredNativeTableOwnerSlides:tables,requiredNativeChartOwnerSlides:[5,7],materializeLiteralChartWorkbooks:true,tableArithmeticContracts:[{slide:9,table:1,label_column:0,total_row:4,value_columns:[1,2,3],component_rows:[1,2,3]}],fontPolicy:{basis:'design',families:['Arial']},verifyArtifactToolImport:true,receiptPath:path.join(buildDir,'validation-v4.json')});
console.log(JSON.stringify(result));
