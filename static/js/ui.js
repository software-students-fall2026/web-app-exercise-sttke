function easeOut(t) 
{
  return 1-Math.pow(1-t,3);
}


function countUp(el) 
{
  var end=parseInt(el.getAttribute("data-count"),10);

  if (isNaN(end) || end<=0) {return;}

  var finalText=el.textContent;

  el.style.display="inline-block";
  el.style.minWidth =el.getBoundingClientRect().width+"px";
  el.textContent="0";
  var start=null;


  function frame(now) 
  {
    if (start===null) 
    {
      start=now;
    }

    var t=Math.min((now-start) /900,1);


    if (t<1) 
    {
      el.textContent=Math.round(end*easeOut(t));
      requestAnimationFrame(frame);
    }

    else 
    {
      el.textContent=finalText;
    }
  }

  requestAnimationFrame(frame);
}


function startCounters() 
{
  var counters=document.querySelectorAll("[data-count]");

  for (var i=0;i<counters.length;i++) 
  {

      countUp(counters[i]);
  }
}


if (!window.matchMedia("(prefers-reduced-motion: reduce)").matches) 
{
  startCounters();
}