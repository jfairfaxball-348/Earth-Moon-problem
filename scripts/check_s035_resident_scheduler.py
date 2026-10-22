from verify_s035_resident_scheduler import main,PROCESSES,stopped
if __name__=="__main__":
 try:main()
 finally:
  for process,area in PROCESSES:
   if process.poll() is None:stopped(process,area)
