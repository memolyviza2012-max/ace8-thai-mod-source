"""Guarded game-specific Offline HUD atlas extension; creates a candidate only."""
import sys,io,struct,json,datetime,hashlib,shutil,subprocess
from pathlib import Path
P=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(P/'05_Scripts_and_Tools/vendor_font_sdf'))
import numpy as np
from scipy.ndimage import distance_transform_edt
from PIL import Image,ImageFont,ImageDraw
from fontTools.ttLib import TTFont
SOURCE=P/'05_Scripts_and_Tools/research_evidence/mission3_offline_font_20261004_142956'
REF=P/'04_Packed_Mod/ClusterRelocation_candidate'
STAGE=P/'04_Packed_Mod'/('OfflineHUD_Light_AA_candidate_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f'))
RETOC=Path(r'E:\Mod_Workspace\Tool\retoc\retoc.exe')
TEXCONV=Path(r'E:\Mod_Workspace\Tool\DirectXTex-may2026\texconv.exe')
NAME='AcesSleipnir-Regular_HUD_OFFLINE'
REL=Path('Live/Content/UI/Font')/NAME
def sha(b):return hashlib.sha256(b).hexdigest()
def run(cmd):
    r=subprocess.run(list(map(str,cmd)),capture_output=True,text=True)
    if r.returncode:raise RuntimeError(r.stdout+'\n'+r.stderr)
    return r.stdout
def main():
    STAGE.mkdir(exist_ok=False)
    asset=(SOURCE/REL.with_suffix('.uasset')).read_bytes();exp=(SOURCE/REL.with_suffix('.uexp')).read_bytes()
    assert len(asset)==1036 and len(exp)==271170
    assert struct.unpack_from('<I',exp,8)[0]==351 and struct.unpack_from('<I',exp,7470)[0]==351
    assert exp[8978:8986]==b'PF_DXT5\0' and exp[-4:]==bytes.fromhex('c1832a9e')
    oldchars=[struct.unpack_from('<iiiiBi',exp,12+i*21) for i in range(351)]
    remap=dict(struct.iter_unpack('<HH',exp[7474:8878]));assert len(remap)==351 and max(remap)==0x45f
    assert struct.unpack_from('<qq',asset,1012)==(262144,262144)
    mapping=json.loads((REF/'Mapping.json').read_text(encoding='utf-8'))
    codes=sorted({ord(c) for value in mapping.values() for c in value}|set(range(0xe01,0xe3b))|set(range(0xe3f,0xe5c)))
    light=P/'03_Font_and_UI/Prompt/Prompt-Light_PUA.ttf'
    f=TTFont(light);cm=dict(f.getBestCmap())
    source_mapping=json.loads((P/'03_Font_and_UI/Mapping.json').read_text(encoding='utf-8'))
    assert source_mapping.keys()==mapping.keys()
    aliases={}
    for key,value in mapping.items():
        original=source_mapping[key];assert len(original)==len(value)
        for a,b in zip(original,value):
            assert ord(a) in cm
            if ord(a)!=ord(b):
                assert ord(b) not in aliases or aliases[ord(b)]==cm[ord(a)]
                aliases[ord(b)]=cm[ord(a)]
    assert all(c not in cm for c in aliases)
    cm.update(aliases)
    for table in f['cmap'].tables:
        if table.isUnicode() and table.format in (4,12):table.cmap={c:g for c,g in cm.items() if table.format==12 or c<=0xffff}
    out=io.BytesIO();f.save(out);ttf=out.getvalue()
    assert f['OS/2'].usWeightClass==300
    codes=[c for c in codes if c in cm and c not in remap];f.close()
    assert all(ord(c) in remap or ord(c) in codes for v in mapping.values() for c in v)
    (STAGE/'Prompt-Light_current_mapping.ttf').write_bytes(ttf)
    font=ImageFont.truetype(io.BytesIO(ttf),36)
    supersample=8
    highfont=ImageFont.truetype(io.BytesIO(ttf),36*supersample)
    width=height=4096
    image=Image.new('RGBA',(width,height),(255,255,255,0))
    additions=[];x=516;y=0;rowheight=0
    glyph_audit=[]
    for code in codes:
        left,top,right,bottom=font.getbbox(chr(code),anchor='ls')
        # FFontCharacter uses USize as text advance. Do not include packing padding.
        # Keep actual advance and account for negative left bearing / mark overhang.
        origin=min(0,left)
        w=max(1,int(np.ceil(max(font.getlength(chr(code)),right)-origin)))
        h=max(1,bottom-top)
        cellw=(w+3)//4*4;cellh=(h+3)//4*4
        if x+cellw>width:x=516 if y<512 else 0;y+=rowheight+4;rowheight=0
        if y<512 and y+cellh>512:y=512;x=0;rowheight=0
        assert y+cellh<=height,'Atlas overflow'
        # Render at 8x, then downsample coverage; do not encode an unconsumed SDF halo.
        high=Image.new('L',(w*supersample,h*supersample),0)
        ImageDraw.Draw(high).text((-origin*supersample,-top*supersample),chr(code),font=highfont,fill=255,anchor='ls')
        mask=high.resize((w,h),Image.Resampling.LANCZOS)
        alpha=np.array(mask);assert alpha.max()>0,'Blank mapped glyph'
        glyph=Image.new('RGBA',(w,h),(255,255,255,0));glyph.putalpha(mask)
        image.paste(glyph,(x,y))
        additions.append((code,(x,y,w,h,0,34+top)))
        glyph_audit.append({'code':hex(code),'glyph_width':w,'advance':float(font.getlength(chr(code))),'alpha_max':int(alpha.max()),'ink_pixels':int(np.count_nonzero(alpha))})
        x+=cellw+4;rowheight=max(rowheight,cellh)
    (STAGE/'glyph_raster_audit.json').write_text(json.dumps(glyph_audit,indent=2),encoding='utf8')
    png=STAGE/'offline_hud_atlas.png';image.save(png)
    run([TEXCONV,'-f','BC3_UNORM','-m','1','-nogpu','-o',STAGE,png])
    dds=(STAGE/'offline_hud_atlas.dds').read_bytes();assert dds[:4]==b'DDS ' and dds[84:88]==b'DXT5'
    assert struct.unpack_from('<II',dds,12)==(height,width)
    compressed=bytearray(dds[128:]);assert len(compressed)==width*height
    # Preserve all original BC3 blocks byte-for-byte at the upper-left corner.
    oldpixels=exp[8998:271142];assert len(oldpixels)==512*512
    for row in range(128):compressed[row*(width//4)*16:row*(width//4)*16+2048]=oldpixels[row*2048:(row+1)*2048]
    # Preserve original records and remap indices; append all Thai/PUA records.
    count=351+len(additions)
    middle=bytearray(exp[7383:7470])
    for original_offset in [7458,7462]:
        assert struct.unpack_from('<I',exp,original_offset)[0]==512
        struct.pack_into('<I',middle,original_offset-7383,width)
    newfont=exp[:8]+struct.pack('<I',count)+exp[12:7383]+b''.join(struct.pack('<iiiiBi',*r) for _,r in additions)+middle+struct.pack('<I',count)+exp[7474:8878]+b''.join(struct.pack('<HH',code,351+i) for i,(code,_) in enumerate(additions))
    texture=bytearray(exp[8878:8998])
    for original_offset in [8888,8892,8962,8966]:
        assert struct.unpack_from('<I',exp,original_offset)[0]==512
        struct.pack_into('<I',texture,original_offset-8878,width)
    # Platform-data skip offset is relative to its field end in this converted asset.
    assert struct.unpack_from('<q',exp,8938)[0]==262220
    struct.pack_into('<q',texture,8938-8878,262220+len(compressed)-len(oldpixels))
    tail=bytearray(exp[271142:-4]);assert len(tail)==24
    struct.pack_into('<II',tail,0,width,height)
    newtexture=texture+compressed+tail
    newexp=newfont+newtexture+exp[-4:]
    header=bytearray(asset)
    # Verified two export records + one inline bulk resource metadata record.
    assert struct.unpack_from('<qq',asset,784)==(8878,1036)
    assert struct.unpack_from('<qq',asset,880)==(262288,9914)
    struct.pack_into('<qq',header,784,len(newfont),1036)
    struct.pack_into('<qq',header,880,len(newtexture),1036+len(newfont))
    struct.pack_into('<qq',header,1012,len(compressed),len(compressed))
    shutil.copytree(REF/'font_input',STAGE/'font_input')
    (STAGE/'font_input'/REL.with_suffix('.uasset')).write_bytes(header)
    (STAGE/'font_input'/REL.with_suffix('.uexp')).write_bytes(newexp)
    # Final table read-back and original block/record preservation checks.
    assert struct.unpack_from('<I',newexp,8)[0]==count and newexp[12:7383]==exp[12:7383]
    map_at=12+count*21+len(middle)
    readmap=dict(struct.iter_unpack('<HH',newexp[map_at+4:len(newfont)]))
    assert len(readmap)==count and all(readmap[k]==v for k,v in remap.items())
    assert all(ord(c) in readmap for value in mapping.values() for c in value)
    for row in range(128):assert compressed[row*(width//4)*16:row*(width//4)*16+2048]==oldpixels[row*2048:(row+1)*2048]
    run([RETOC,'to-zen',STAGE/'font_input',STAGE/'pakchunk0-Windows_999_P.utoc','--version','UE5_4'])
    (STAGE/'pakchunk0-Windows_999_P.pak').rename(STAGE/'retoc_empty_placeholder.pak')
    verify=STAGE/'verify_containers';verify.mkdir()
    game=Path(r'F:\SteamLibrary\steamapps\common\ACE COMBAT 8\Game\Content\Paks')
    for name in ['global.utoc','global.ucas']:shutil.copy2(game/name,verify/name)
    for suffix in ['utoc','ucas']:shutil.copy2(STAGE/('pakchunk0-Windows_999_P.'+suffix),verify)
    run([RETOC,'to-legacy',verify,STAGE/'roundtrip','--no-shaders'])
    for path in (STAGE/'font_input').rglob('*.uexp'):
        assert path.read_bytes()==(STAGE/'roundtrip'/path.relative_to(STAGE/'font_input')).read_bytes()
    report={'stage':str(STAGE),'thai_font':'Prompt Light','weight_class':300,'raster_mode':'8x supersampled alpha coverage, no SDF halo or metric padding','original_font_records':351,'added_glyphs':len(additions),'all_current_mapping_codes_present':True,'atlas_dimensions':[width,height],'original_characters_remap_and_BC3_blocks_preserved':True,'font_payload_roundtrip_identical':True,'runtime_verified':False,'game_modified':False,'candidate_containers':[{'name':p.name,'sha256':sha(p.read_bytes())} for p in STAGE.glob('pakchunk*')]}
    (STAGE/'validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
