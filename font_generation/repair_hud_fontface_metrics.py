"""Restore native vertical metrics in the runtime HUD FontFace; preserve glyphs and QA text."""
from pathlib import Path
import argparse,datetime,hashlib,io,json,shutil,stat,struct,subprocess
from fontTools.ttLib import TTFont
P=Path(__file__).resolve().parent.parent
ap=argparse.ArgumentParser();ap.add_argument('--install',action='store_true');args=ap.parse_args()
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7)));stamp=now.strftime('%Y%m%d_%H%M%S_%f')
S=P/'04_Packed_Mod'/('HUD_FontFaceMetrics_candidate_'+stamp);S.mkdir(exist_ok=False)
BASE=P/'04_Packed_Mod/OfflineHUD_Light_AA_candidate_20261004_213120_241545'
ORIG=P/'05_Scripts_and_Tools/research_evidence/aces_font_legacy'
REL=Path('Live/Content/UI/Font/0710_AcesSleipnirTextHUD-Regular')
pointer=P/'04_Packed_Mod/current_deployment_manifest.json';previous=Path(json.loads(pointer.read_text(encoding='utf8'))['manifest']);old=json.loads(previous.read_text(encoding='utf8'));G=Path(old['game_root']).resolve()
def sha(b):return hashlib.sha256(b).hexdigest()
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf8')
def run(cmd):
 r=subprocess.run(list(map(str,cmd)),capture_output=True,timeout=120)
 if r.returncode:raise RuntimeError(r.stdout.decode(errors='replace')+'\n'+r.stderr.decode(errors='replace'))
 return r.stdout
def closed():
 if int(run(['powershell','-NoProfile','-Command','@(Get-Process -Name AceCombat8,start_protected_game -ErrorAction SilentlyContinue).Count']).strip()):raise RuntimeError('Game running; candidate retained; close game before installing')
def sfnt(b):
 starts=[i for i in range(4,len(b)-4) if b[i:i+4] in (b'OTTO',b'\x00\x01\x00\x00') and i+struct.unpack_from('<I',b,i-4)[0]==len(b)-4]
 assert len(starts)==1 and b[-4:]==bytes.fromhex('c1832a9e');return starts[0],b[starts[0]:-4]
def metrics(f):
 return {'unitsPerEm':f['head'].unitsPerEm,'hhea':{k:getattr(f['hhea'],k) for k in ['ascent','descent','lineGap']},'OS_2':{k:getattr(f['OS/2'],k) for k in ['version','sTypoAscender','sTypoDescender','sTypoLineGap','usWinAscent','usWinDescent','fsSelection']}}
origexp=(ORIG/REL.with_suffix('.uexp')).read_bytes();exp=(BASE/'font_input'/REL.with_suffix('.uexp')).read_bytes();asset=(BASE/'font_input'/REL.with_suffix('.uasset')).read_bytes()
_,originalttf=sfnt(origexp);start,oldttf=sfnt(exp);original=TTFont(io.BytesIO(originalttf));font=TTFont(io.BytesIO(oldttf),recalcTimestamp=False)
before=metrics(font);reference=metrics(original)
assert reference['hhea']=={'ascent':963,'descent':-245,'lineGap':100}
assert before['hhea']=={'ascent':1180,'descent':-422,'lineGap':0}
assert reference['unitsPerEm']==before['unitsPerEm']==1000
for table in ['hhea','OS_2']:
 name='OS/2' if table=='OS_2' else table
 for k,v in reference[table].items():setattr(font[name],k,v)
out=io.BytesIO();font.save(out,reorderTables=False);newttf=out.getvalue();check=TTFont(io.BytesIO(newttf),recalcTimestamp=False)
assert metrics(check)==reference
priorfont=TTFont(io.BytesIO(oldttf));assert priorfont.getBestCmap()==check.getBestCmap()
assert priorfont.getGlyphOrder()==check.getGlyphOrder()
for tag in priorfont.keys():
 if tag not in ['GlyphOrder','head','hhea','OS/2']:assert priorfont.getTableData(tag)==check.getTableData(tag),tag
assert priorfont['head'].yMin==check['head'].yMin and priorfont['head'].yMax==check['head'].yMax
newexp=exp[:start-4]+struct.pack('<I',len(newttf))+newttf+exp[-4:]
header=bytearray(asset)
def uniqueq(value):
 needle=struct.pack('<q',value);positions=[i for i in range(len(asset)-7) if asset[i:i+8]==needle];assert len(positions)==1;return positions[0]
struct.pack_into('<q',header,uniqueq(len(exp)-4),len(newexp)-4)
struct.pack_into('<q',header,uniqueq(len(asset)+len(exp)-4),len(asset)+len(newexp)-4)
shutil.copytree(BASE/'font_input',S/'font_input')
(S/'font_input'/REL.with_suffix('.uexp')).write_bytes(newexp)
(S/'font_input'/REL.with_suffix('.uasset')).write_bytes(header)
# Save both inspected TTFs privately as evidence; no proprietary original assets are published.
(S/'HUD_original.ttf').write_bytes(originalttf);(S/'HUD_before.ttf').write_bytes(oldttf);(S/'HUD_native_metrics.ttf').write_bytes(newttf)
retoc=Path(r'E:\Mod_Workspace\Tool\retoc\retoc.exe')
run([retoc,'to-zen',S/'font_input',S/'pakchunk0-Windows_999_P.utoc','--version','UE5_4'])
(S/'pakchunk0-Windows_999_P.pak').rename(S/'retoc_empty_placeholder.pak')
verify=S/'verify_containers';verify.mkdir()
for name in ['global.utoc','global.ucas']:shutil.copy2(G/'Game/Content/Paks'/name,verify/name)
for suffix in ['utoc','ucas']:shutil.copy2(S/('pakchunk0-Windows_999_P.'+suffix),verify)
run([retoc,'to-legacy',verify,S/'roundtrip','--no-shaders'])
for f in (S/'font_input').rglob('*.uexp'):assert f.read_bytes()==(S/'roundtrip'/f.relative_to(S/'font_input')).read_bytes()
mapping=json.loads((P/'04_Packed_Mod/ClusterRelocation_candidate/Mapping.json').read_text(encoding='utf8'))
cm=check.getBestCmap();assert all(ord(c) in cm for value in mapping.values() for c in value)
report={'stage':str(S),'target_font':REL.as_posix(),'before_metrics':before,'original_and_candidate_metrics':reference,'before_hhea_span_em':1.602,'native_hhea_span_em':1.208,'native_hhea_span_with_gap_em':1.308,'glyph_outlines_hmtx_cmap_and_all_nonmetric_tables_unchanged':True,'font_payload_roundtrip_identical':True,'all_current_mapping_codes_present':True,'previous_offline_atlas_height_experiment_reverted':True,'offline_atlas_restored_to_accepted_2_3':True,'other_FontFaces_unchanged':True,'QA_translation_untouched':True,'diagnosis':'Runtime HUD FontFace inherited expanded Prompt metrics; original Latin outlines retained but vertical layout metrics were not. Restore HUD-specific original metrics, not widget coordinates. User runtime test required.','runtime_verified':False,'game_launched':False}
save(S/'validation.json',report)
if not args.install:print(json.dumps(report,indent=2));raise SystemExit(0)
closed();saved={}
for r in old['targets']:
 f=(G/r['relative_path']).resolve();assert f.is_relative_to(G);b=f.read_bytes();assert sha(b)==r['installed_sha256'];saved[r['relative_path']]=b
saved['EasyAntiCheat/Settings.json']=(G/'EasyAntiCheat/Settings.json').read_bytes();assert sha(saved['EasyAntiCheat/Settings.json'])==old['original_settings_sha256']
cp=P/'01_Original_Backup'/('checkpoint_HUD_fontface_metrics_'+stamp);cp.mkdir(exist_ok=False)
for rel,b in saved.items():
 f=cp/'GameDirectory'/rel;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(b);assert f.read_bytes()==b;f.chmod(stat.S_IREAD)
save(cp/'checkpoint_manifest.json',{'previous_manifest':str(previous),'game_root':str(G),'backups':[{'path':r,'sha256':sha(b)} for r,b in saved.items()]});(cp/'checkpoint_manifest.json').chmod(stat.S_IREAD)
log=P/'05_Scripts_and_Tools/session_log.md'
with log.open('a',encoding='utf8') as f:f.write(f'\n## [{now.isoformat()}] CHECKPOINT BEFORE WRITE — HUD runtime FontFace native metrics\n- {cp}: all {len(saved)-1} authored files plus Settings verified/read-only. Prior offline-atlas maxheight candidate did not fix position per user screenshot; reverted its glyph resizing. Patch only 0710 HUD FontFace hhea and OS/2 vertical metrics to original (963/-245, gap100; fsSelection192). All glyphs, advances, cmap and other nonmetric tables identical. Retoc round-trip passes. Only two font containers change, QA PAK stays. Runtime alignment acceptance pending.\n')
closed()
for rel,b in saved.items():assert (G/rel).read_bytes()==b
changes={'Game/Content/Paks/pakchunk0-Windows_999_P.'+s:(S/('pakchunk0-Windows_999_P.'+s)).read_bytes() for s in ['utoc','ucas']};done=[]
try:
 for rel,b in changes.items():done.append(rel);(G/rel).write_bytes(b);assert (G/rel).read_bytes()==b
 for rel,b in saved.items():
  if rel not in changes:assert (G/rel).read_bytes()==b
except Exception:
 for rel in done:(G/rel).write_bytes(saved[rel])
 raise
manifest={**old,'checkpoint':str(cp),'previous_manifest':str(previous),'timestamp_bangkok':now.isoformat(),'purpose':'HUD runtime FontFace original vertical metrics candidate; previous offline height experiment rejected','font_stage':str(S),'targets':[{**r,'installed_sha256':sha(changes[r['relative_path']]),'bytes':len(changes[r['relative_path']])} if r['relative_path'] in changes else r for r in old['targets']],'gameplay_verified':False,'runtime_font_verified':False,'offline_hud_runtime_verified':False,'game_launched':False,'translation_user_accepted':True}
save(S/'deployment_manifest.json',manifest);save(pointer,{'manifest':str(S/'deployment_manifest.json')});save(S/'installation_report.json',{'checkpoint':str(cp),'changed_files':list(changes),'all_other_authored_files_unchanged':True,'original_settings_preserved':True,'QA_PAK_unchanged':True,'game_launched':False})
with log.open('a',encoding='utf8') as f:f.write('- Installed two containers and verified hashes, all other authored files and Settings unchanged. No game launch/screen control.\n')
print(json.dumps({**report,'installed':True,'checkpoint':str(cp)},indent=2))
