# -*- coding: utf-8 -*-
import FWCore.ParameterSet.Config as cms
process = cms.Process("L1TMuonEmulation")
import os
import sys
import commands

process.load("FWCore.MessageLogger.MessageLogger_cfi")

process.MessageLogger = cms.Service("MessageLogger",
        # suppressInfo       = cms.untracked.vstring('AfterSource', 'PostModule'),
        destinations=cms.untracked.vstring(
                                               # 'detailedInfo',
                                               # 'critical',
                                               'cout',
                                               #'cerr',
                                               # 'omtfEventPrint'
                    ),
        categories=cms.untracked.vstring('l1tMuBayesEventPrint', 'OMTFReconstruction'), #, 'FwkReport'
        cout=cms.untracked.PSet(
                         threshold=cms.untracked.string('INFO'),
                         default=cms.untracked.PSet(limit=cms.untracked.int32(0)),
                         # INFO   =  cms.untracked.int32(0),
                         # DEBUG   = cms.untracked.int32(0),
                         l1tMuBayesEventPrint=cms.untracked.PSet(limit=cms.untracked.int32(1000000000)),
                         OMTFReconstruction=cms.untracked.PSet(limit=cms.untracked.int32(1000000000)),
                         #FwkReport=cms.untracked.PSet(reportEvery = cms.untracked.int32(50) ),
                       ), 
       debugModules=cms.untracked.vstring('simBayesOmtfDigis') 
       # debugModules = cms.untracked.vstring('*')
    )

#process.MessageLogger.cerr.FwkReport.reportEvery = cms.untracked.int32(50)
process.options = cms.untracked.PSet(wantSummary=cms.untracked.bool(False))

process.source = cms.Source('PoolSource',
 #fileNames = cms.untracked.vstring('file:/afs/cern.ch/work/g/gflouris/public/SingleMuPt6180_noanti_10k_eta1.root')
 #fileNames = cms.untracked.vstring('file:///afs/cern.ch/work/k/kbunkow/private/omtf_data/SingleMu_15_p_1_1_qtl.root')    
 #fileNames = cms.untracked.vstring('file:///eos/user/k/kbunkow/cms_data/mc/PhaseIIFall17D/SingleMu_PU200_32DF01CC-A342-E811-9FE7-48D539F3863E_dump500Events.root')
                        fileNames = cms.untracked.vstring("file:///eos/cms/store/user/folguera/P2L1TUpgrade/Mu_FlatPt2to100-pythia8-gun_file.root")
 )
	                    
process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(1000))

# PostLS1 geometry used
process.load('Configuration.Geometry.GeometryExtended2015Reco_cff')
process.load('Configuration.Geometry.GeometryExtended2015_cff')
############################
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_condDBv2_cff')
from Configuration.AlCa.GlobalTag_condDBv2 import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, 'auto:run2_mc', '')


####Event Setup Producer
process.load('L1Trigger.L1TMuonOverlapPhase1.fakeOmtfParams_cff')
process.esProd = cms.EDAnalyzer("EventSetupRecordDataGetter",
   toGet = cms.VPSet(
      cms.PSet(record = cms.string('L1TMuonOverlapParamsRcd'),
               data = cms.vstring('L1TMuonOverlapParams'))
                   ),
   verbose = cms.untracked.bool(False)
)

process.TFileService = cms.Service("TFileService", fileName = cms.string('omtfAnalysis1.root'), closeFileFast = cms.untracked.bool(True) )
								
####OMTF Emulator
process.load('L1Trigger.L1TMuonOverlapPhase1.simBayesOmtfDigis_cfi')

process.simBayesOmtfDigis.dumpResultToXML = cms.bool(True)
process.simBayesOmtfDigis.rpcMaxClusterSize = cms.int32(3)
process.simBayesOmtfDigis.rpcMaxClusterCnt = cms.int32(2)
process.simBayesOmtfDigis.rpcDropAllClustersIfMoreThanMax = cms.bool(True)
process.simBayesOmtfDigis.dumpHitsToROOT = cms.bool(True)
process.simBayesOmtfDigis.dumpHitsFileName = cms.string('OMTFHits_P1TP.root')

process.simBayesOmtfDigis.lctCentralBx = cms.int32(8);#<<<<<<<<<<<<<<<<!!!!!!!!!!!!!!!!!!!!TODO this was changed in CMSSW 10(?) to 8. if the data were generated with the previous CMSSW then you have to use 6

#process.simBayesOmtfDigis.goldenPatternResultFinalizeFunction = cms.int32(6) #valid values are 0, 1, 2, 3, 5, 6, but for other then 0 the candidates quality assignemnt must be updated

process.dumpED = cms.EDAnalyzer("EventContentAnalyzer")
process.dumpES = cms.EDAnalyzer("PrintEventSetupContent")

process.L1TMuonSeq = cms.Sequence( process.esProd          
                                   + process.simBayesOmtfDigis 
                                   #+ process.dumpED
                                   #+ process.dumpES
)

process.L1TMuonPath = cms.Path(process.L1TMuonSeq)

process.out = cms.OutputModule("PoolOutputModule", 
                               fileName = cms.untracked.string("l1tomtf_superprimitives1.root"),
                               outputCommands=cms.untracked.vstring(
                                   'drop *',
                                   "keep *_dtTrigger*_*_*",
                                   "keep *_simDtTrigger*_*_*",
                                   "keep *_simBayesOmtfDigis_OMTF_L1TMuonEmulation",
                                   "keep *_genParticles_*_*", 
                                   )
)

process.output_step = cms.EndPath(process.out)
process.schedule = cms.Schedule(process.L1TMuonPath)
process.schedule.extend([process.output_step])
