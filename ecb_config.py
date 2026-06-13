# ECB API Configuration
# 欧洲央行数据API - 美国VPS直连可用，国内需代理
ECB_BASE = "https://sdw-wsrest.ecb.europa.eu/service"

# 常用数据流
ECB_ENDPOINTS = {
    "EUR_USD": "/data/EXR/D.USD.EUR.SP00.A",           # 欧元/美元汇率
    "HICP": "/data/ICP/M.U2.Y.000000.3.INX",            # 欧元区调和CPI
    "ECB_RATE": "/data/FM/B.U2.EUR.4F.KR.MRR_FR.LEV",  # ECB主要再融资利率
    "GDP": "/data/MNA/Q.N.I9.W2.S1.S1.B.B1GQ._Z._Z._Z.S.V.N._T.IX",  # 欧元区GDP
}
