from zone.IDL.thrift.CanParserNode.ttypes import *
from zone.IDL.thrift.CanStackNode.ttypes import *
from zone.IDL.thrift.CommonNode import Result
from zone.dsc import (
    CanPdu,
    CanConfig,
    CrcRcConfig,
    ConvertInput,
    PduCrcRcConfig,
    CanMessage,
    PduMessage,
    PduMessages,
    DbPath,
    PduUpdate,
    CanMessages,
    Channel,
    SubscribeInfo,
)
from .utils.dsx import as_list
from .utils.snippets import normalize_components

from zone.clients import (
    canstackclient,
    canparserclient,
    linstackclient,
    linparserclient,
)


class App(object):
    """
    App docstring.
    """

    def __init__(
        self,
        *,
        configs=None,
        connections=None,
        canstack=None,
        canparser=None,
        linstack=None,
        linparser=None,
        data=None
    ) -> None:
        """

        :param configs:
        :param connections:
        :param canstack:
        :param canparser:
        :param linstack:
        :param linparser:
        :param data:
        """
        self._configs = as_list(configs)
        self._connections = as_list(connections)
        self._clients = []
        self._canstack = canstack or canstackclient
        self._canparser = canparser or canparserclient
        self._linstack = linstack or linstackclient
        self._linparser = linparser or linparserclient
        self._data = data
        self._clients = {
            "canstack": self._canstack,
            "canparser": self._canparser,
            "linstack": self._linstack,
            "linparser": self._linparser,
        }

    @property
    def Configs(self):
        return self._configs

    @Configs.setter
    def Configs(self, value):
        self._configs = as_list(value)

    @property
    def Connections(self):
        return self._connections

    @Connections.setter
    def Connections(self, value):
        self._connections = as_list(value)

    @property
    def CanStack(self):
        return self._canstack

    @CanStack.setter
    def CanStack(self, value):
        self._canstack = value

    @property
    def CanParser(self):
        return self._canparser

    @CanParser.setter
    def CanParser(self, value):
        self._canparser = value

    @property
    def LinStack(self):
        return self._linstack

    @LinStack.setter
    def LinStack(self, value):
        self._linstack = value

    @property
    def LinParser(self):
        return self._linparser

    @LinParser.setter
    def LinParser(self, value):
        self._linparser = value

    @property
    def Clients(self):
        return self._clients

    @property
    def DataModel(self):
        return self._data

    # api
    def connect(self, components: list = None) -> dict:
        """

        :param components: 列表。可以的值是"canstack", "canparser", "linstack", "linparser"。

        例如["canstack", "canparser"]。 当只有一个元素时候可以单纯写字符串，例如"canstack"。

        :return: Result
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`

        例如：

            connect("canstack") or

            connect(["canstack", "canparser"])

        """
        if components is None:
            components = ["all"]
        components = as_list(components)
        norm_comps = normalize_components(components)
        results = {}
        for i in norm_comps:
            if self._clients[i] is not None:
                print(self._clients[i])
                result = self._clients[i].connect()
                print(result)
                results[i] = result
        return results

    def connect_all(self) -> dict:
        """

        :return: Result
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`


        """
        return self.connect()

    def disconnect(self, components: list = None) -> dict:
        """

        :param components:

        :return: Result
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`


        """
        if components is None:
            components = ["all"]
        components = as_list(components)
        norm_comps = normalize_components(components)
        results = {}
        for i in norm_comps:
            if self._clients[i] is not None:
                print(self._clients[i])
                result = self._clients[i].disconnect()
                print(result)
                results[i] = result
        return results

    def disconnect_all(self) -> dict:
        """

        :return: Result
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`


        """
        return self.disconnect()

    def getStatus(self, components: list = None) -> dict:
        """

        :param components:

        :return: Result
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`


        """
        if components is None:
            components = ["all"]
        components = as_list(components)
        norm_comps = normalize_components(components)
        results = {}
        for i in norm_comps:
            if self._clients[i] is not None:
                print(self._clients[i])
                result = self._clients[i].getStatus()
                print(result)
                results[i] = result
        return results

    def setCrcRcConfig(self, req: CrcRcConfig) -> Result:
        # canstack and canparser
        """

        :param req: CrcRcConfig实例

        :return: Result
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`


        """
        ret = self._canstack.setCrcRcConfig(req)
        ret = self._canparser.setCanParserCrcRcConfig(req)
        return ret

    def clearCrcRcConfig(self, req: CrcRcConfig) -> Result:
        # canstack and canparser
        """

        :param req:

        :return: Result
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`


        """
        ret = self._canstack.clearCrcRcConfig(req)
        ret = self._canparser.clearCrcRcConfig(req)
        return ret

    def clearAllCrcRcConfig(self) -> Result:
        # canstack and canparser
        # todo
        """

        :return: Result
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`


        """
        ret = self._canstack.clearAllCrcRcConfig()
        ret = self._canparser.clearAllCrcRcConfig()
        return ret

    def checkAlive(self, components: list = None) -> dict:
        """

        :param components:

        :return: Result
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`


        """
        if components is None:
            components = ["all"]
        components = as_list(components)
        norm_comps = normalize_components(components)
        results = {}
        for i in norm_comps:
            if self._clients[i] is not None:
                print(self._clients[i])
                result = self._clients[i].checkAlive()
                print(result)
                results[i] = result
        return results

    def start(self, components: list = None) -> Result:
        """

        :param components:

        :return: Result
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`


        """
        if components is None:
            components = ["all"]
        components = as_list(components)
        norm_comps = normalize_components(components)
        results = {}
        for i in norm_comps:
            if self._clients[i] is not None:
                if hasattr(self._clients[i], "start") and callable(
                    getattr(self._clients[i], "start")
                ):
                    result = self._clients[i].start()
                    results[i] = result
        return results

    def stop(self, components: list = None) -> Result:
        """

        :param components:

        :return: Result
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`


        """
        if components is None:
            components = ["all"]
        components = as_list(components)
        norm_comps = normalize_components(components)
        results = {}
        for i in norm_comps:
            if self._clients[i] is not None:
                if hasattr(self._clients[i], "stop") and callable(
                    getattr(self._clients[i], "stop")
                ):
                    result = self._clients[i].checkAlive()
                    results[i] = result
        return results

    # # can stack

    def getVersion(self) -> Result:
        """

        :return: Result
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`


        """
        return self._canstack.getVersion()

    def setCanConfig(self, req: CanConfig) -> Result:
        """

        :param req:

        :return: Result
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`


        """
        ret = self._canparser.setCanConfig(req)
        ret = self._canstack.setConfigs(req)
        return ret

    def sendCanPdu(self, req: CanPdu) -> Result:
        """

        :param req:

        :return: Result
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`


        """
        self._canparser.updateCanPdu(req)
        self._canparser.sendCanPduCyc(req)

    def stopCanPdu(self, req: CanPdu) -> Result:
        """

        :param req:

        :return: Result
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`


        """
        self._canparser.sendCanPduCyc(req)

    def setConfigs(self, req: CanConfig) -> Result:
        """

        :param req: CanConfig

        :return: Result
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`


        """
        return self._canstack.setConfigs(req)

    def startCanStack(self) -> Result:
        """

        :return: Result
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`


        """
        return self._canstack.startCanStack()

    def stopCanStack(self) -> Result:
        """

        :return: Result
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`


        """
        return self._canstack.stopCanStack()

    def clearCanSend(self) -> Result:
        """

        :return: Result
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`


        """
        return self._canstack.clearCanSend()

    def clearCanAllCrcRcConfig(self) -> Result:
        """

        :return: Result
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`


        """
        return self._canstack.clearAllCrcRcConfig()

    def sendCanMessageCyc(self, req: CanMessage) -> Result:
        """

        :param req:

        :return: Result
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`


        """
        return self._canstack.sendCanMessageCyc(req)

    def sendCanMessage(self, req: CanMessage) -> Result:
        """

        :param req:

        :return: Result
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`


        """
        return self._canstack.sendCanMessage(req)

    def sendCanMessages(self, req: CanMessages, stmin: int) -> Result:
        """

        :param req:
        :param stmin:

        :return: Result
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`


        """
        return self._canstack.sendCanMessages(req, stmin)

    def getStackStatus(self) -> Result:
        """

        :return: Result
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`


        """
        return self._canstack.getStatus()

    def stopChannelSendCyc(self, req: Channel) -> Result:
        """

        :param req:

        :return: Result
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`


        """
        return self._canstack.stopChannelSendCyc(req)

    def sendCan(self, req: CanMessage) -> Result:
        """

        :param req:

        :return: Result
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`


        """
        return self._canstack.sendCan(req)

    def getChannelBusloadCurrent(self, req: Channel) -> Result:
        """

        :param req:

        :return: Result
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`


        """
        return self._canstack.getChannelBusloadCurrent(req)

    def getChannelBusloadMax(self, req: Channel) -> Result:
        """

        :param req:

        :return: Result
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`


        """
        return self._canstack.getChannelBusloadMax(req)

    def getChannelBusloadAvg(self, req: Channel) -> Result:
        """

        :param req:

        :return: Result
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`


        """
        return self._canstack.getChannelBusloadAvg(req)

    def getChannelErrorFrameTotal(self, req: Channel) -> Result:
        """

        :param req:

        :return: Result
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`


        """
        return self._canstack.getChannelErrorFrameTotal(req)

    # # can parser

    def clearAllCanParserCrcRcConfig(self) -> Result:
        """

        :return: Result
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`


        """
        return self._canparser.clearAllCanParserCrcRcConfig()

    def clearCanParserCrcRcConfig(self, req: PduCrcRcConfig) -> Result:
        """

        :param req:

        :return: Result
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`


        """
        return self._canparser.clearCanParserCrcRcConfig(req)

    def sendCanFrameCyc(self, req: CanMessage) -> Result:
        """

        :param req:

        :return: Result
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`


        """
        return self._canparser.sendCanFrameCyc(req)

    def sendCanPduCyc(self, req: PduMessage) -> Result:
        """

        :param req:

        :return: Result
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`


        """
        return self._canparser.sendCanPduCyc(req)

    def sendCanPduCycList(self, req: PduMessages) -> Result:
        """

        :param req:

        :return: Result
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`


        """
        return self._canparser.sendCanPduCycList(req)

    def addDbFile(self, req: DbPath) -> Result:
        """

        :param req:

        :return: Result
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`


        """
        return self._canparser.addDbFile(req)

    def getCanDbConfigs(self) -> Result:
        """

        :return: Result
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`


        """
        return self._canparser.getCanDbConfigs()

    def getCanDbPath(self) -> Result:
        """

        :return: Result
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`


        """
        return self._canparser.getCanDbPath()

    def subscribeMsg(self, req: SubscribeInfo) -> Result:
        """

        :param req:

        :return: Result
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`


        """
        return self._canparser.subscribeMsg(req)

    def unSubscribeMsg(self, req: SubscribeInfo) -> Result:
        """

        :param req:

        :return: Result
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`


        """
        return self._canparser.unSubscribeMsg(req)

    def getCanDbInfo(self) -> Result:
        """

        :return: Result
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`


        """
        return self._canparser.getCanDbInfo()

    def clear(self) -> Result:
        """

        :return: Result
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`


        """
        return self._canparser.clear()

    def clearCanStackSubscribe(self) -> Result:
        """

        :return: Result
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`


        """
        return self._canparser.clearCanStackSubscribe()

    def encodePdu(self, req) -> Result:
        """

        :param req:

        :return: Result
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`


        """
        return self._canparser.encodePdu(req)

    def convertCanDbToPy(self, req: ConvertInput) -> Result:
        """

        :param req:

        :return: Result
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`


        """
        return self._canparser.convertCanDbToPy(req)

    def convertCanDbToJson(self, req: ConvertInput) -> Result:
        """

        :param req:

        :return: Result
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`


        """
        return self._canparser.convertCanDbToJson(req)

    def updateCanPdu(self, req: PduUpdate) -> Result:
        """

        :param req:

        :return: Result
        :rtype: :class:`~zone.IDL.thrift.CommonNode.Result`


        """
        return self._canparser.updateCanPdu(req)

    # todo, the following are to be implemented...
    # # lin stack
    #
    # def reset(self):
    #     return self._linstack.reset()
    #
    # def setLinConfig(self, req):
    #     return self._linstack.setLinConfig(req)
    #
    # def setChannelConig(self, req):
    #     return self._linstack.setChannelConig(req)
    #
    # def startLinStack(self):
    #     return self._linstack.startLinStack()
    #
    # def stopLinStack(self):
    #     return self._linstack.stopLinStack()
    #
    # def setMessageSimulation(self, req):
    #     return self._linstack.setMessageSimulation(req)
    #
    # def setHeaderSimulation(self, req):
    #     return self._linstack.setHeaderSimulation(req)
    #
    # def setMessageData(self, req):
    #     return self._linstack.setMessageData(req)
    #
    # def getLinStatus(self):
    #     return self._linstack.getLinStatus()
    #
    # def clearLinSubscribe(self):
    #     return self._linstack.clearLinSubscribe()
    #
    # def clearLinSend(self, req):
    #     return self._linstack.clearLinSend()
    #
    # def setLinCrcConfig(self, req):
    #     return self._linstack.clearLinSend(req)
    #
    # def clearLinCrcConfig(self, req):
    #     return self._linstack.clearLinCrcConfig(req)
    #
    # def getDeltaTime(self):
    #     return self._linstack.getDeltaTime()
    #
    # # # lin parser
    #
    # def addDbfile(self, req):
    #     return self._linparser.addDbfile(req)
    #
    # def setChannelConfig(self, req):
    #     return self._linparser.setChannelConfig(req)
    #
    # def setNodeSimulation(self, req):
    #     return self._linparser.setNodeSimulation(req)
    #
    # def setFrameSimulation(self, req):
    #     return self._linparser.setFrameSimulation(req)
    #
    # def setFrameData(self, req):
    #     return self._linparser.setFrameData(req)
    #
    # def SetSignalData(self, req):
    #     return self._linparser.SetSignalData(req)
    #
    # def clearCanParserSubscribe(self):
    #     return self._linparser.clearCanParserSubscribe()
    #
    # def clearDbfile(self):
    #     return self._linparser.clearDbfile()
    #
    # def getLinParserStatus(self):
    #     return self._linparser.getLinParserStatus()
    #
    # def getLdfJsonTree(self):
    #     return self._linparser.getLdfJsonTree()
    #
    # def convertLinDbToPy(self, req):
    #     return self._linparser.convertLinDbToPy(req)
    #
    # def convertLinDbToJson(self, req):
    #     return self._linparser.convertLinDbToJson(req)
    #
    # def setCrcConfig(self, req):
    #     return self._linparser.setCrcConfig(req)
    #
    # def clearCrcConfig(self, req):
    #     return self._linparser.clearCrcConfig(req)


if __name__ == "__main__":
    pass
