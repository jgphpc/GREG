#
#  Description: This module contains a class, PatReport.
#
#  Filename:   PatReport.py
#
#         written by JaeHyuk Kwack (jkwack2@illinois.edu)
#                    Blue Waters Scientific and Engineering Applications Support (SEAS) Group
#                    National Center for Supercomputing Applications - NCSA
#                    University of Illinois at Urbana-Champaign
# ------------------------------------------------------------------------------------------------------------------

## Importing Libraries
from __future__ import division
from CrayPat.PatRegion import PatRegion

class PatReport:
   def __init__(self,fname,nThread):
      self.fname=fname
      self.nThread=nThread
      self.read_PatReport()

   def read_PatReport(self):
      # Reading the CrayPat report
      print ("   Reading %s"%self.fname)
      fpat = open(self.fname,'r')
      A = fpat.readlines()
      fpat.close()

      # Reading number of compute node
      for line in A:
         line_split = line.split()
         if len(line_split) != 0:
            if ''.join(line_split[0:5]) == 'NumberofPEs(MPIranks):':
               nMPI = int(line_split[5].replace(",",""))
            if ''.join(line_split[0:5]) == 'NumbersofPEsperNode:':
               nMPIperNode = int(line_split[5].replace(",",""))
               break
      nNode = nMPI/nMPIperNode
      print ('   Number of MPI ranks          = %d '%(nMPI) )
      print ('   Number of MPI ranks per Node = %d '%(nMPIperNode) )
      print ('   Number of Compute Node       = %d '%(nNode) )
      print ('   Number of Threads            = %d '%(self.nThread) )

      # Counting number of user pat_regions
      Regions= []
      for i,line in enumerate(A):
         line_split = line.split()
         if len(line_split) != 0:
            if line_split[0] == '==============================================================================':
               if A[i+2].split()[0] == '------------------------------------------------------------------------------':
                  word = ''.join(A[i+1].split())
                  Regions.append(PatRegion(word,nNode,self.nThread,i,A))

      # Discarding Regions with CI = 0
      Regions_core = []
      for i,R in enumerate(Regions):
         if R.CI_L1_DCA*R.CI_DCR_Good != 0:
            Regions_core.append(R)
      self.Regions = Regions_core
      for R in self.Regions:
         R.show()

   def write_csv(self):
      # Write Pat_Regions to a CSV file
      fname_out =self.fname+'_data.csv'
      print ('   Writing CrayPat data to %s file'%fname_out)
      fcsv = open(fname_out,'w')
      fcsv.write('title,time_percentage,time,OPS,L1_DCA,L1_DCA_based_CI,DCR_Good,DCR_Good_based_CI,GFLOP/s/node\n')
      for R in self.Regions:
         fcsv.write('%s,%f,%f,%d,%d,%f,%d,%f,%f\n'%(R.title,R.Time_percentage,R.Time,R.PAPI_FP_OPS,R.PAPI_L1_DCA,R.CI_L1_DCA,R.DCR_Good,R.CI_DCR_Good,R.GFLOPS_per_Node))
      fcsv.close()
