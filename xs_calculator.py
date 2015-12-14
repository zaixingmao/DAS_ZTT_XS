#!/usr/bin/env python
import ROOT as r

defaultOrder = [("Diboson", r.TColor.GetColor(222, 90,106)),
                ("WJets",  r.TColor.GetColor(100,182,232)),
                ('TTJets', r.TColor.GetColor(155,152,204)),
                ('QCD', r.TColor.GetColor(250,202,255)),
                ("DY", r.TColor.GetColor(248,206,104))]


def buildHistDict(nbins):
    histDict = {}
    for iSample, iColor in defaultOrder:
        histDict[iSample+'_OST'] = r.TH1F(iSample+'_OST', '', nbins, 0, 300)
        histDict[iSample+'_OST'].SetFillColor(iColor)
        histDict[iSample+'_OST'].SetMarkerColor(iColor)
        histDict[iSample+'_OST'].SetMarkerStyle(21)
        histDict[iSample+'_OST'].SetLineColor(r.kBlack)
        histDict[iSample+'_OSR'] = r.TH1F(iSample+'_OSR', '', nbins, 0, 300)
        histDict[iSample+'_OSR'].SetFillColor(iColor)
        histDict[iSample+'_OSR'].SetMarkerColor(iColor)
        histDict[iSample+'_OSR'].SetMarkerStyle(21)
        histDict[iSample+'_OSR'].SetLineColor(r.kBlack)
    histDict['data_OST'] = r.TH1F('data_OST', '', nbins, 0, 300)
    histDict['data_OST'].SetMarkerStyle(8)
    histDict['data_OST'].SetMarkerSize(0.9)
    histDict['data_OST'].SetMarkerColor(r.kBlack)

    histDict['data_OSR'] = r.TH1F('data_OSR', '', nbins, 0, 300)
    histDict['data_OSR'].SetMarkerStyle(8)
    histDict['data_OSR'].SetMarkerSize(0.9)
    histDict['data_OSR'].SetMarkerColor(r.kBlack)

    histDict['DY_SST'] = r.TH1F('DY_SST', '', nbins, 0, 300)
    histDict['DY_SSR'] = r.TH1F('DY_SSR', '', nbins, 0, 300)
    return histDict

def setMyLegend(lPosition, lHistList):
    l = r.TLegend(lPosition[0], lPosition[1], lPosition[2], lPosition[3])
    l.SetFillStyle(0)
    l.SetBorderSize(0)
    for i in range(len(lHistList)):
        l.AddEntry(lHistList[i][0], lHistList[i][1], lHistList[i][2])
    return l

def getBins(hist, mass_low, mass_high):
    bin_low = -1
    bin_high = -1
    for i in range(hist.GetNbinsX()):
        if hist.GetBinCenter(i+1) >= mass_low and bin_low == -1:
            bin_low = i+1
        if hist.GetBinCenter(i+1) >= mass_high and bin_high == -1:
            bin_high = i
        if bin_low != -1 and bin_high != -1:
            return bin_low, bin_high
    return bin_low, bin_high

def buildStackDict(histDict, xs_T, xs_R):
    stackDict = {}
    stackDict['OST'] = r.THStack()
    stackDict['OSR'] = r.THStack()
    
    for iSample, iColor in defaultOrder:
        scale = 1.0
        if iSample != 'DY':
            stackDict['OST'].Add(histDict[iSample+'_OST'])
            stackDict['OSR'].Add(histDict[iSample+'_OSR'])
        else:
            tmpOST = histDict['DY_OST'].Clone()
            tmpOSR = histDict['DY_OSR'].Clone()
            tmpOST.Scale(xs_T/6025.2)
            tmpOSR.Scale(xs_R/6025.2)
            stackDict['OST'].Add(tmpOST)
            stackDict['OSR'].Add(tmpOSR)
    return stackDict

def FillHisto(input, output, weight = 1.0):
    for i in range(input.GetNbinsX()):
        output.Fill(input.GetBinCenter(i+1), input.GetBinContent(i+1)*weight)

def buildLegendDict(histDict, position, XS_OST, XS_OSR):
    legendDict = {}
    histList = {'T': [], 'R': []}
    histList['T'].append((histDict['data_OST'], 'Observed', 'lep'))
    histList['R'].append((histDict['data_OSR'], 'Observed', 'lep'))
    for iSample, iColor in reversed(defaultOrder):
        if iSample == 'DY':        
            histList['T'].append((histDict[iSample+'_OST'], "%s (xs = %.1f pb)" %(iSample, XS_OST), 'f'))
            histList['R'].append((histDict[iSample+'_OSR'], "%s (xs = %.1f pb)" %(iSample, XS_OSR), 'f'))
        else:
            histList['T'].append((histDict[iSample+'_OST'], iSample, 'f'))
            histList['R'].append((histDict[iSample+'_OSR'], iSample, 'f'))

    legendDict['T'] = setMyLegend(position, histList['T'])
    legendDict['R'] = setMyLegend(position, histList['R'])
    return legendDict


def xs_calculator(fileList = [], mass_low = 25, mass_high = 125, nbins = 12):

    print 'Estimating Z->ll xs in visible mass region (%.1f, %.1f)' %(mass_low, mass_high)

    ZTT_OST = 0.0 #data - all other bkg in opposite sign tight tau isolation region
    ZTT_OSR = 0.0 #data - all other bkg in opposite sign relaxed tau isolation region
    QCD_SST = 0.0 #data - all other bkg in same sign tight tau isolation region
    QCD_SSR = 0.0 #data - all other bkg in same sign relaxed tau isolation region
    DY_OST = 0.0
    DY_OSR = 0.0
    DY_SST = 0.0
    DY_SSR = 0.0

    QCD_SS_to_OS_SF = 1.06

    histDict = buildHistDict(nbins)
    #loop over all the samples
    for iFileName, iFileLocation in fileList:
        isData = False
        if iFileName == 'data':
            isData = True
        isDY = False
        if iFileName == 'DY':
            isDY = True

        ifile = r.TFile(iFileLocation)
        weight = -1.0
        if isData:
            weight = 1.0

        lowBin, highBin = getBins(ifile.Get('visibleMassOS'), mass_low, mass_high)
        FillHisto(ifile.Get('visibleMassOS'), histDict[iFileName+'_OST'])
        FillHisto(ifile.Get('visibleMassOSRelaxedTauIso'), histDict[iFileName+'_OSR'])

        if not isDY:
            ZTT_OST += weight*ifile.Get('visibleMassOS').Integral(lowBin, highBin)
            ZTT_OSR += weight*ifile.Get('visibleMassOSRelaxedTauIso').Integral(lowBin, highBin)
            QCD_SST += weight*ifile.Get('visibleMassSS').Integral(lowBin, highBin)
            QCD_SSR += weight*ifile.Get('visibleMassSSRelaxedTauIso').Integral(lowBin, highBin)
            FillHisto(ifile.Get('visibleMassSS'), histDict['QCD_OST'], weight)
            FillHisto(ifile.Get('visibleMassSSRelaxedTauIso'), histDict['QCD_OSR'], weight)
        else:
            FillHisto(ifile.Get('visibleMassSS'), histDict['DY_SST'])
            FillHisto(ifile.Get('visibleMassSSRelaxedTauIso'), histDict['DY_SSR'])
            DY_OST += ifile.Get('visibleMassOS').Integral(lowBin, highBin)
            DY_OSR += ifile.Get('visibleMassOSRelaxedTauIso').Integral(lowBin, highBin)
#         print iFileName, ifile.Get('visibleMassOS').Integral()

    lowBin, highBin = getBins(histDict['DY_SST'], mass_low, mass_high)
    XS_OST = 6025.2*(ZTT_OST - QCD_SST*QCD_SS_to_OS_SF)/(DY_OST-QCD_SS_to_OS_SF*histDict['DY_SST'].Integral(lowBin, highBin))
    XS_OSR = 6025.2*(ZTT_OSR - QCD_SSR*QCD_SS_to_OS_SF)/(DY_OSR-QCD_SS_to_OS_SF*histDict['DY_SSR'].Integral(lowBin, highBin)) 

    histDict['QCD_OSR'].Add(histDict['DY_SSR'], -1.0*XS_OSR/6025.2)
    histDict['QCD_OSR'].Scale(QCD_SS_to_OS_SF)
    histDict['QCD_OST'].Add(histDict['DY_SST'], -1.0*XS_OST/6025.2)
    histDict['QCD_OST'].Scale(QCD_SS_to_OS_SF)

    stackDict = buildStackDict(histDict, XS_OST, XS_OSR)
    legendDict = buildLegendDict(histDict, (0.6, 0.8 - 0.06*4, 0.85, 0.8), XS_OST, XS_OSR)

    #plot
    pdf = 'xs.pdf'
    c = r.TCanvas("c","Test", 800, 600)
    max_t = 1.2*max(stackDict['OST'].GetMaximum(), histDict['data_OST'].GetMaximum())
    stackDict['OST'].Draw('hist H')
    stackDict['OST'].SetTitle('OS Tight Tau Iso; visibleMass; events')
    stackDict['OST'].SetMaximum(max_t)
    stackDict['OST'].GetYaxis().SetTitleOffset(1.2)
    histDict['data_OST'].Draw('same PE')
    legendDict['T'].Draw('same')
    c.Print('%s(' %pdf)

    max_t = 1.2*max(stackDict['OSR'].GetMaximum(), histDict['data_OSR'].GetMaximum())
    stackDict['OSR'].Draw('hist H')
    stackDict['OSR'].SetTitle('OS Relaxed Tau Iso; visibleMass; events')
    stackDict['OSR'].SetMaximum(max_t)
    stackDict['OSR'].GetYaxis().SetTitleOffset(1.2)
    histDict['data_OSR'].Draw('same PE')
    legendDict['R'].Draw('same')
    c.Print('%s)' %pdf)

    print 'DY->ll xs in tight region: %.1f pb' %XS_OST
    print 'DY->ll xs in relaxed region: %.1f pb' %XS_OSR


dirName = '/afs/cern.ch/user/z/zmao/CMSSW_7_1_16/src//Tau-CMSDAS/ntuples/'

fileList = [('DY', '%s/tot_job_spring15_ggNtuple_DYJetsToLL_M-50_amcatnlo_pythia8_25ns_miniAOD.root' %dirName),
            ('TTJets', '%s/tot_job_spring15_ggNtuple_TTJets_amcatnlo_pythia8_25ns_miniAOD.root' %dirName),
            ('WJets', '%s/tot_job_spring15_ggNtuple_WJetsToLNu_amcatnlo_pythia8_25ns_miniAOD.root' %dirName),
#            ('WW', '%s/tot_job_spring15_ggNtuple_WWTo2L2Nu_powheg_25ns_miniAOD.root' %dirName),
#            ('WZ', '%s/tot_job_spring15_ggNtuple_WZTo3LNu_powheg_pythia8_25ns_miniAOD.root' %dirName),
#            ('ZZ', '%s/tot_job_spring15_ggNtuple_ZZTo4L_powheg_pythia8_25ns_miniAOD.root' %dirName),
            ('data', '%s/tot_job_SingleMu_Run2015D_TOT.root' %dirName),
            ]

xs_calculator(fileList = fileList, mass_low = 25, mass_high = 125, nbins = 12)
