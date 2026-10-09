ps -u checker -o pid,etime,time,pcpu,rss,args --sort=-pcpu | head -6 | cut -c1-150
