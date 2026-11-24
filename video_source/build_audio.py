import subprocess, json, sys
OLD_END={'s0':4,'s1':12,'s2':12,'s3':9,'s4':9,'s5':12,'s6':9,'s7':9,'s8':4}   # old scene lengths
ORDER=['s0','s1','s2','s3','s4','s5','s6','s7','s8']
L=[ # scene, old_anchor, text
('s0',0.7,"Salom! Bugun makkajo'xori masalasini qadamma-qadam yechamiz."),
('s1',0.4,"Makkajo'xorida ikki n teng yigirma. Ikki yuz qirqta mikrosporotsit meyoz bilan bo'lindi."),
('s1',3.2,"Hosil bo'lgan mikrosporalarning yigirma besh foizi changga aylanmadi."),
('s1',5.6,"Qolgan changlarning uchdan bir qismi urug'lanishda qatnashdi."),
('s1',8.2,"Urug'lanishda qatnashgan spermiylardagi jami xromosomalar sonini toping."),
('s2',0.6,"Birinchi qadam. Bitta mikrosporotsit meyozda bo'linganda to'rtta mikrospora hosil bo'ladi."),
('s2',7.2,"Demak, ikki yuz qirqni to'rtga ko'paytiramiz. To'qqiz yuz oltmishta mikrospora."),
('s3',0.4,"Ikkinchi qadam. Yigirma besh foizi chang bo'lmadi, demak yetmish besh foizi chang bo'ldi."),
('s3',5.4,"To'qqiz yuz oltmishni nol butun yetmish beshga ko'paytiramiz. Yetti yuz yigirmata chang."),
('s4',0.3,"Uchinchi qadam. Qolgan changlarning uchdan bir qismi qatnashdi."),
('s4',4.4,"Yetti yuz yigirmani uchga bo'lamiz. Ikki yuz qirqta chang."),
('s5',0.4,"To'rtinchi qadam. Har bir changda ikkitadan spermiy bor."),
('s5',4.0,"Gulli o'simliklarda qo'sh urug'lanish bo'ladi: bitta spermiy tuxum hujayra bilan, ikkinchisi markaziy hujayra bilan qo'shiladi."),
('s5',7.4,"Ikki yuz qirqni ikkiga ko'paytiramiz. To'rt yuz sakson spermiy."),
('s6',0.5,"Beshinchi qadam. Spermiy gaploid hujayra, shuning uchun n teng o'n."),
('s6',4.2,"To'rt yuz sakson ko'paytirilsin o'nga. To'rt ming sakkiz yuz xromosoma."),
('s7',0.5,"Natijalar. Birinchi qadam: to'qqiz yuz oltmishta mikrospora."),
('s7',1.4,"Ikkinchi qadam: yetti yuz yigirmata chang."),
('s7',2.3,"Uchinchi qadam: ikki yuz qirqta chang."),
('s7',3.2,"To'rtinchi qadam: to'rt yuz sakson spermiy."),
('s7',4.1,"Beshinchi qadam: to'rt ming sakkiz yuz."),
('s7',5.4,"Javob: to'rt ming sakkiz yuz ta xromosoma."),
('s8',0.9,"Yechim tugadi. Keyingi masalada ko'rishamiz."),
]
speed=sys.argv[1] if len(sys.argv)>1 else '150'
GAP=0.45; TAILMIN=1.3
dur=[]
for i,(s,o,t) in enumerate(L):
    f=f'tts/n{i:02d}.wav'
    subprocess.run(['espeak-ng','-v','uz','-s',speed,'-p','42','-a','180','-w',f,t],check=True)
    dur.append(float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f])))
T=0.0; TL=[]; A={}; clips=[]
idx=0
for sc in ORDER:
    mine=[(i,L[i]) for i in range(len(L)) if L[i][0]==sc]
    s0=T; anchors=[]; cur=s0+(mine[0][1][1] if sc=='s0' else 0.5)
    for k,(i,(s,o,t)) in enumerate(mine):
        anchors.append([o,cur-s0]); clips.append((f'tts/n{i:02d}.wav',cur,dur[i]))
        cur+=dur[i]+GAP
    last_end=cur-GAP
    old_last=mine[-1][1][1]; new_last=anchors[-1][1]
    end=max(s0+new_last+(OLD_END[sc]-old_last), last_end+TAILMIN)
    TL.append([sc,round(s0,3),round(end,3)]); A[sc]=anchors; T=end
total=round(T+0.4,3)
json.dump({'TL':TL,'A':A,'TOTAL':total},open('vid_bio/plan.json','w'))
open('vid_bio/plan.js','w').write('window.PLAN='+json.dumps({'TL':TL,'A':A,'TOTAL':total})+';')
print(TL,total)
# mix
cmd=['ffmpeg','-v','error','-y']
for f,st,d in clips: cmd+=['-i',f]
fl=[]
for i,(f,st,d) in enumerate(clips): fl.append(f'[{i}:a]adelay={int(st*1000)}|{int(st*1000)},volume=1.0[a{i}]')
fl.append(''.join(f'[a{i}]' for i in range(len(clips)))+f'amix=inputs={len(clips)}:normalize=0,apad=whole_dur={total}[m]')
cmd+=['-filter_complex',';'.join(fl),'-map','[m]','-t',str(total),'-ar','44100','-ac','1','narration.wav']
subprocess.run(cmd,check=True)
print('audio ok')
