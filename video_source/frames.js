const {chromium}=require('playwright');const fs=require('fs');
(async()=>{
 const FPS=20;fs.mkdirSync('frames',{recursive:true});
 const b=await chromium.launch();const p=await b.newPage({viewport:{width:720,height:1280}});
 p.on('pageerror',e=>console.log('ERR',e.message));
 await p.goto('file://'+process.cwd()+'/index.html');await p.waitForTimeout(500);
 const N=Math.round(80*FPS);
 for(let i=0;i<N;i++){await p.evaluate(t=>render(t),i/FPS);
  await p.screenshot({path:`frames/f${String(i).padStart(5,'0')}.jpg`,type:'jpeg',quality:92});}
 await b.close();console.log('done',N);
})();
