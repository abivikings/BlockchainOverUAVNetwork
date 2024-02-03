import ns.applications
import ns.core
import ns.flow_monitor
import ns.internet
import ns.mobility
import ns.network
import ns.olsr
import ns.wifi
import ns.csma
import ns.netanim
import sys
from blockchain import *
from store_data_in_db import *
from functools import reduce


def network(transaction_pool_len, nod, transaction_pool, directory_log, nodi, req_n, transaction_list_len, f_node_list):
    Results = None
    wifi = ns.wifi.WifiHelper()
    wifiMac = ns.wifi.WifiMacHelper()
    wifiPhy = ns.wifi.YansWifiPhyHelper()
    wifiChannel = ns.wifi.YansWifiChannelHelper.Default()
    wifiPhy.SetChannel(wifiChannel.Create())
    ssid = ns.wifi.Ssid("wifi-default")
    wifiMac.SetType ("ns3::AdhocWifiMac",
                     "Ssid", ns.wifi.SsidValue(ssid))

    internet = ns.internet.InternetStackHelper()
    list_routing = ns.internet.Ipv4ListRoutingHelper()
    olsr_routing = ns.olsr.OlsrHelper()
    static_routing = ns.internet.Ipv4StaticRoutingHelper()
    list_routing.Add(static_routing, 0)
    list_routing.Add(olsr_routing, 100)
    internet.SetRoutingHelper(list_routing)

    ipv4Addresses = ns.internet.Ipv4AddressHelper()
    ipv4Addresses.SetBase(ns.network.Ipv4Address("10.0.0.0"), ns.network.Ipv4Mask("255.255.255.0"))


    csma = ns.csma.CsmaHelper()

    addresses = []
    nodes = []
    status_nodes = []

    minX = 245
    maxX = 200
    minY = 245
    maxY = 200
    minZ = 245
    maxZ = 200
    
    area = (maxX - minX) * (maxY - minY)
    height = maxZ - minZ
    
    area_string = str(minX) + "|" + str(maxX) + "|" + str(minY) + "|" + str(maxY) + "|" + str(minZ) + "|" + str(maxZ)

    for xi in range(nod):
        node = ns.network.Node()
        nodes.append(node)
        status_node = ns.network.NodeContainer(node)

        internet.Install(status_node)
    
        mobility = ns.mobility.MobilityHelper()
        mobility.SetMobilityModel("ns3::GaussMarkovMobilityModel",
                            "Bounds", ns.core.StringValue(area_string),
                            "TimeStep", ns.core.TimeValue(ns.core.Seconds(0.5)),
                            "Alpha", ns.core.DoubleValue(0.85),
                            "MeanVelocity", ns.core.StringValue("ns3::UniformRandomVariable[Min=800|Max=1200]"),
                            "MeanDirection", ns.core.StringValue("ns3::UniformRandomVariable[Min=0|Max=6.283185307]"),
                            "MeanPitch", ns.core.StringValue("ns3::UniformRandomVariable[Min=0.05|Max=0.05]"),
                            "NormalVelocity", ns.core.StringValue("ns3::NormalRandomVariable[Mean=0.0|Variance=0.0|Bound=0.0]"),
                            "NormalDirection", ns.core.StringValue("ns3::NormalRandomVariable[Mean=0.0|Variance=0.2|Bound=0.4]"),
                            "NormalPitch", ns.core.StringValue("ns3::NormalRandomVariable[Mean=0.0|Variance=0.02|Bound=0.04]"))

    
        mobility.SetPositionAllocator("ns3::RandomBoxPositionAllocator",
                                    "X", ns.core.StringValue("ns3::UniformRandomVariable[Min=0|Max=100]"),
                                    "Y", ns.core.StringValue("ns3::UniformRandomVariable[Min=0|Max=100]"),
                                    "Z", ns.core.StringValue("ns3::UniformRandomVariable[Min=0|Max=100]"))
        
        mobility.Install (status_node)
        
        devices = wifi.Install(wifiPhy, wifiMac, node)
        ipv4_interfaces = ipv4Addresses.Assign(devices)
        addresses.append(ipv4_interfaces.GetAddress(0))
        status_nodes.append(status_node)
        pass

    payloadSize  = blockchain(transaction_pool_len, nod, transaction_pool, directory_log, nodi, req_n, transaction_list_len, f_node_list)

    datarate = input("Data Rate : ")
    port = 9   # Discard port(RFC 863)
    onOffHelper = ns.applications.OnOffHelper("ns3::UdpSocketFactory",
                                  ns.network.Address(ns.network.InetSocketAddress(ns.network.Ipv4Address("10.0.0.1"), port)))
    onOffHelper.SetAttribute("DataRate", ns.network.DataRateValue(ns.network.DataRate(str(datarate) + "kbps")))
    onOffHelper.SetAttribute("OnTime", ns.core.StringValue ("ns3::ConstantRandomVariable[Constant=1]"))
    onOffHelper.SetAttribute("OffTime", ns.core.StringValue ("ns3::ConstantRandomVariable[Constant=0]"))
    onOffHelper.SetAttribute ("PacketSize", ns.core.UintegerValue(payloadSize))


    for i, node in enumerate(status_nodes):
        destaddr = addresses[(len(addresses) - 1 - i) % len(addresses)]
        #print (i, destaddr)
        onOffHelper.SetAttribute("Remote", ns.network.AddressValue(ns.network.InetSocketAddress(destaddr, port)))
        app = onOffHelper.Install(ns.network.NodeContainer(node))
        urv = ns.core.UniformRandomVariable()
        app.Start(ns.core.Seconds(urv.GetValue(20, 30)))
        wifiPhy.EnablePcap("fnet_blockchain", node)
        

    print ("Configure Tracing.")
    anim = ns.netanim.AnimationInterface("fnet_blockchain.xml")
    ascii = ns.network.AsciiTraceHelper()


    stream = ascii.CreateFileStream("fnet_blockchain.tr")
    wifiPhy.EnableAsciiAll(stream)
    csma.EnableAsciiAll(stream)
    internet.EnableAsciiIpv4All(stream)
    csma.EnablePcapAll("fnet_blockchain", False)


    #internet.EnablePcapAll("wifi-olsr")
    flowmon_helper = ns.flow_monitor.FlowMonitorHelper()
    #flowmon_helper.SetMonitorAttribute("StartTime", ns.core.TimeValue(ns.core.Seconds(31)))
    monitor = flowmon_helper.InstallAll()
    monitor = flowmon_helper.GetMonitor()
    monitor.SetAttribute("DelayBinWidth", ns.core.DoubleValue(0.001))
    monitor.SetAttribute("JitterBinWidth", ns.core.DoubleValue(0.001))
    monitor.SetAttribute("PacketSizeBinWidth", ns.core.DoubleValue(20))

    ns.core.Simulator.Stop(ns.core.Seconds(100))
    ns.core.Simulator.Run()


    total_throughput_list = []
    total_delay_list = []

    def print_stats(os, st):
        print ("  Tx Bytes: ", st.txBytes, file=os)
        print ("  Rx Bytes: ", st.rxBytes, file=os)
        print ("  Tx Packets: ", st.txPackets, file=os)
        print ("  Rx Packets: ", st.rxPackets, file=os)
        print ("  Lost Packets: ", st.lostPackets, file=os)
        if st.rxPackets > 0:
            print ("  Mean{Delay}: ", (st.delaySum.GetSeconds() / st.rxPackets), file=os)
            print ("  Mean{Jitter}: ", (st.jitterSum.GetSeconds() / (st.rxPackets)), file=os)
            print ("  Mean{Hop Count}: ", float(st.timesForwarded) / st.rxPackets + 1, file=os)
            total_delay_list.append((st.delaySum.GetSeconds() / st.rxPackets))

        if 0:
            print ("Delay Histogram", file=os)
            for i in range(st.delayHistogram.GetNBins () ):
              print (" ",i,"(", st.delayHistogram.GetBinStart (i), "-", \
                  st.delayHistogram.GetBinEnd (i), "): ", st.delayHistogram.GetBinCount (i), file=os)
            print ("Jitter Histogram", file=os)
            for i in range(st.jitterHistogram.GetNBins () ):
              print (" ",i,"(", st.jitterHistogram.GetBinStart (i), "-", \
                  st.jitterHistogram.GetBinEnd (i), "): ", st.jitterHistogram.GetBinCount (i), file=os)
            print ("PacketSize Histogram", file=os)
            for i in range(st.packetSizeHistogram.GetNBins () ):
              print (" ",i,"(", st.packetSizeHistogram.GetBinStart (i), "-", \
                  st.packetSizeHistogram.GetBinEnd (i), "): ", st.packetSizeHistogram.GetBinCount (i), file=os)

        for reason, drops in enumerate(st.packetsDropped):
            print ("  Packets dropped by reason %i: %i" % (reason, drops), file=os)
        #for reason, drops in enumerate(st.bytesDropped):
        #    print "Bytes dropped by reason %i: %i" % (reason, drops)

    monitor.CheckForLostPackets()
    classifier = flowmon_helper.GetClassifier()
    stats = monitor.GetFlowStats()
    if Results is None:
        for flow_id, flow_stats in stats:
            t = classifier.FindFlow(flow_id)
            proto = {6: 'TCP', 17: 'UDP'} [t.protocol]
            print ("FlowID: %i (%s %s/%s --> %s/%i)" % \
                (flow_id, proto, t.sourceAddress, t.sourcePort, t.destinationAddress, t.destinationPort))          
            
            print_stats(sys.stdout, flow_stats)
            #print throughput
            rxBytes = flow_stats.rxBytes
            txTime = flow_stats.timeLastRxPacket.GetSeconds() - flow_stats.timeFirstTxPacket.GetSeconds()
            throughput = rxBytes * 8 / txTime / 1e6  # Mbps
            print("Flow ID %d throughput: %0.2f Mbps" % (flow_id, throughput))
            total_throughput_list.append(throughput)
    else:
        print (monitor.SerializeToXmlFile(Results, True, True))

    if len(total_delay_list) > 0:
        delay_count = reduce(lambda x, y: x + y, total_delay_list)
        avg_delay = delay_count/len(total_delay_list)
        
    
        throuhtput_count = reduce(lambda x, y: x + y, total_throughput_list)
        throughtput = throuhtput_count/len(total_throughput_list)
        
        print("All nodes are in "+ str(area) + " m3 and height from ground " + str(height) + " m")

        InserGraphData(nod, payloadSize, avg_delay, throughtput, transaction_list_len, datarate)

    return 0

def blockchain(transaction_pool_len, nod, transaction_pool, directory_log, nodi, req_n, transaction_list_len, f_node_list):
    payloadSize = 0
    
    nod, backboneNodes, throughtput, avg_delay = compute_blockchain(transaction_pool_len, nod, transaction_pool, directory_log, nodi, req_n, transaction_list_len, f_node_list)

        
    csv_file_path = '/home/sojib/ns-allinone-3.36.1/ns-3.36.1/test_logs/blockchain_1.csv'  # Replace with the path to your folder containing CSV files

    if os.path.exists(csv_file_path):
        payloadSize = os.path.getsize(csv_file_path)
    else:
        print(f"The file '{csv_file_path}' does not exist.")

    print("Below result is calculating for transaction : "+ str(nod) + " and packet size : " + str(payloadSize) + " kbps")
    

    return payloadSize

if __name__ == '__main__':
    payloadSize = 0
    
    # chain variables
    current_directory = os.getcwd()
    directory_main = current_directory+'/test'
    directory_log = current_directory+'/test_logs'


    pat = current_directory+'/test_logs_pool/*'
    pat_r = glob.glob(pat)
    for i in pat_r:
        os.remove(i)


    file_node_1 = directory_log+"/blockchain_"+str(1)+".csv"
    isExist = os.path.exists(file_node_1)

    log_node_1 = directory_log+"/node_"+str(1)+".log"
    isExistLog = os.path.exists(log_node_1)
    node_max_len = 100

    #no of node
    nod = no_of_node_input(node_max_len)
    nodi = nod + 1


    transaction_pool_directory = open(directory_main+"/transaction_pool.log", "r")
    transaction_content = transaction_pool_directory.read()


    # transaction_list = ConvertToList(transaction_content)
    trasaction_input = input("Number of transaction : ")
    transaction_list = [i for i in range(0, int(trasaction_input))]
    transaction_list_len = len(transaction_list)

    # faulty node list 
    f_node_list = []

    # print(type(transaction_list))
    print(f"Transactions: {transaction_content} \n")

    transaction_pool = round_robin_gen_2(nod,transaction_list,f_node_list)
    print(f"Round Robin Transaction pool: {transaction_pool} \n")

    transaction_pool_len = len(transaction_pool)
    transaction_pool_len_inc = transaction_pool_len +1

    if not isExist:
        myblockchain = Blockchain()
        myblockchain.generate_genesis_block()
        main_chain = myblockchain.get_chain()

        # when bockchain is not exist
        for x in range(1,nodi):
            save(directory_log+"/blockchain_"+str(x)+".csv",main_chain)
    else:
        dl_chain = directory_log+"/blockchain_1.csv"
        chain_results = pd.read_csv(dl_chain)

        # when blockchain exist
        for x in range(1,nodi):
            if x in f_node_list:
                continue
            else:         
                dl_chain_w = directory_log+"/blockchain_"+str(x)+".csv"
                chain_results.to_csv(dl_chain_w, index = False)        
            
            
    # when node log not exist we create all log for each node
    if not isExistLog:
        for x in range(1,nodi):
            f=open(directory_log+"/node_"+str(x)+".log", "w")
            f.write('')
            f.close()


    # faulty node calculate
    f= (nod-1)/3
    # print(f)
    req_n = (2*f) + 1
    
    network(transaction_pool_len, nod, transaction_pool, directory_log, nodi, req_n, transaction_list_len, f_node_list)