const {chromium}=require('playwright');const fs=require('fs');const {spawn}=require('child_process');
const TL=fs.readFileSync('timeline.json','utf8');
fs.writeFileSync('built.html',fs.readFileSync('page.html','utf8').replace('/*TIMELINE*/null',TL));
const T=JSON.parse(TL).T, FPS=30;
async function page(b){const p=await b.newPage({viewport:{width:1080,height:1920},deviceScaleFactor:1});
  p.on('pageerror',e=>console.error('PAGEERR',e.message));p.on('console',m=>{if(m.type()==='error')console.error('CONSOLE',m.text())});
  await p.goto('file://'+process.cwd()+'/built.html');await p.evaluate(()=>window.ready());return p;}
(async()=>{
  const mode=process.argv[2];const b=await chromium.launch();
  if(mode==='stills'){const p=await page(b);
    for(const t of process.argv[3].split(',').map(Number)){await p.evaluate(([t])=>render(t,Math.round(t*30)),[t]);
      await p.screenshot({path:`still_${t.toFixed(2)}.jpg`,type:'jpeg',quality:80});}
  } else { // segment render: idx of N
    const N=+process.argv[3], i=+process.argv[4];const nf=Math.ceil(T*FPS);
    const f0=Math.floor(nf*i/N), f1=Math.floor(nf*(i+1)/N);const p=await page(b);
    const ff=spawn('ffmpeg',['-v','error','-y','-f','image2pipe','-framerate',String(FPS),'-c:v','mjpeg','-i','-','-c:v','libx264','-preset','medium','-crf','16','-pix_fmt','yuv420p',`seg_${i}.mp4`],{stdio:['pipe','inherit','inherit']});
    for(let f=f0;f<f1;f++){await p.evaluate(([t,f])=>render(t,f),[f/FPS,f]);
      const buf=await p.screenshot({type:'jpeg',quality:93});
      if(!ff.stdin.write(buf)) await new Promise(r=>ff.stdin.once('drain',r));
      if((f-f0)%150===0) console.log(`seg${i} ${f-f0}/${f1-f0}`);}
    ff.stdin.end();await new Promise(r=>ff.on('close',r));
  }
  await b.close();
})();
