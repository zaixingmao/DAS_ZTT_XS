#!/usr/bin/env python
import ROOT as r

Lumi = 2.1

def xs_calculator(fileList = []):
    ZTT_OST = 0.0 #data - all other bkg in opposite sign tight tau isolation region
    ZTT_OSR = 0.0 #data - all other bkg in opposite sign relaxed tau isolation region
    OCD_SST = 0.0 #data - all other bkg in same sign tight tau isolation region
    QCD_SSR = 0.0 #data - all other bkg in same sign relaxed tau isolation region

    #loop over all the samples
    for iFileName, iFileLocation in fileList:
        isData = False
        if iFileName == 'data':
            isData = True
        ifile = r.TFile(iFileLocation)
        weight = -1.0
        if isData:
            weight = 1.0

        ZTT_OST += weight*file.Get('visibleMassOS').Integral()
        ZTT_OSR += weight*file.Get('visibleMassOSRelaxedTauIso').Integral()
        QCD_SST += weight*file.Get('visibleMassSS').Integral()
        QCD_SSR += weight*file.Get('visibleMassSSRelaxedTauIso').Integral()

    XS_OST = (ZTT_OST - QCD_SST)/Lumi
    XS_OSR = (ZTT_OSR - QCD_SSR)/Lumi
    return XS_OST, XS_OSR