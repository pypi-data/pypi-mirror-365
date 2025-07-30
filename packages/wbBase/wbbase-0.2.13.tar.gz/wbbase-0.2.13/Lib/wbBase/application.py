"""WorkBench Application"""
from __future__ import annotations

import inspect
import logging
import mmap
import os
import pickle
import sys
import tempfile
import time
from argparse import ArgumentParser, Namespace
from importlib import metadata, resources
from io import BytesIO
from typing import TYPE_CHECKING, ClassVar, List, Optional, Union

import wx
from wx.adv import (
    SPLASH_CENTER_ON_SCREEN,
    SPLASH_NO_TIMEOUT,
    ShowTip,
    SplashScreen,
    TipProvider,
)

from .applicationInfo import ApplicationInfo
from .applicationWindow import ApplicationWindow
from .artprovider import Artprovider
from .document import DOC_SILENT, dbg
from .pluginManager import PluginManager
from .scripting import execfile, execsource
from .shortcut import shortcutsFromConfig

try:
    from git import GitCommandError, InvalidGitRepositoryError
    from git.repo import Repo

    has_git = True
except ImportError:
    has_git = False

if TYPE_CHECKING:
    from types import FunctionType

    from .applicationWindow import ApplicationWindow
    from .document.manager import DocumentManager
    from .panelManager import PanelManager

log = logging.getLogger(__name__)

AppInfo_None = 0
AppInfo_AppName = 1
AppInfo_VendorName = 2


class ExtChangeTestTimer(wx.Timer):
    """
    Timer for test of external changes
    """

    @property
    def app(self) -> App:
        """
        The running Workbench application.
        """
        return wx.GetApp()

    def Notify(self):
        self.app.documentManager.testForExternalChanges(testAll=True)


class ListenAndLoadTimer(wx.Timer):
    """
    Timer to check if document should be loaded
    """

    @property
    def app(self) -> App:
        """
        The running Workbench application.
        """
        return wx.GetApp()

    def Notify(self):
        self.Stop()
        sharedMemory = self.app._sharedMemory
        sharedMemory.seek(0)
        if sharedMemory.read_byte() == ord("+"):  # available data
            topWin = self.app.TopWindow
            if not topWin.IsIconized():
                topWin.Iconize(True)
            topWin.Iconize(False)
            topWin.Raise()
            data = sharedMemory.read(1024 - 1)
            sharedMemory.seek(0)
            sharedMemory.write_byte(
                ord("*")
            )  # finished reading, set buffer free marker
            sharedMemory.flush()
            args = pickle.loads(data)
            for arg in args:
                if os.path.exists(arg):
                    topWin.documentManager.CreateDocument(arg, DOC_SILENT)
            topWin.RequestUserAttention()
        self.Start(200)


class AppSplashScreen(SplashScreen):
    """
    Window with a thin border, displaying a bitmap describing the application.
    Shown in application initialization.
    """
    def __init__(
        self,
        bitmap: wx.Bitmap,
        splashStyle: int,
        milliseconds: int,
        id: int = wx.ID_ANY,
        pos: wx.Point = wx.DefaultPosition,
        size: wx.Size = wx.DefaultSize,
        style: int = wx.BORDER_SIMPLE | wx.FRAME_NO_TASKBAR | wx.STAY_ON_TOP,
    ):
        super().__init__(
            bitmap, splashStyle, milliseconds, None, id, pos, size, style
        )
        position = wx.Point(0, bitmap.Height - 20)
        size = wx.Size(bitmap.Width, 20)
        self.message = wx.StaticText(
            self,
            wx.ID_ANY,
            "Loading App ...",
            position,
            size,
            wx.ALIGN_CENTER_HORIZONTAL | wx.ST_ELLIPSIZE_MIDDLE | wx.TRANSPARENT_WINDOW,
        )

    def setMessage(self, text: str) -> None:
        self.message.SetLabel(text)


class ResourceTipProvider(TipProvider):
    """
    TipProvider with tips loaded from application resources.
    """
    def __init__(self, currentTip:int):
        super().__init__(currentTip)
        self._currentTyp = currentTip
        self.tips:List[str] = []
        tips = self.app.getResource("tips.txt")
        if isinstance(tips, str):
            self.tips = tips.splitlines()

    @property
    def app(self) -> App:
        """
        The running Workbench application.
        """
        return wx.GetApp()

    @property
    def hasTips(self) -> bool:
        """True is any tips are available."""
        return len(self.tips) > 0

    def GetCurrentTip(self) -> int:
        return self._currentTyp

    def GetTip(self) -> str:
        tip = self.tips[self._currentTyp]
        self._currentTyp += 1
        if self._currentTyp >= len(self.tips) -1:
            self._currentTyp = 0
        return tip
    

class App(wx.App):
    """
    Implements the main application object
    """

    # modes for external changes test
    EXT_CHANGE_TEST_ON_REQUEST: ClassVar[int] = 0
    EXT_CHANGE_TEST_ON_ACTIVATE: ClassVar[int] = 1
    EXT_CHANGE_TEST_ON_TIMER: ClassVar[int] = 2
    pluginManagerClass: ClassVar[type[PluginManager]] = PluginManager
    topWindowClass: ClassVar[type[ApplicationWindow]] = ApplicationWindow
    resourceContainerName: ClassVar[str] = "data"
    TopWindow: ApplicationWindow
    Traits: wx.AppTraits
    extChangeTimer: ExtChangeTestTimer
    listenAndLoadTimer: ListenAndLoadTimer
    config: wx.ConfigBase
    instanceChecker: wx.SingleInstanceChecker

    _post_init_queue: List[FunctionType] = []

    def __init__(
        self,
        debug: int = 0,
        iconName: str = wx.ART_EXECUTABLE_FILE,
        test: bool = False,
        info: Optional[ApplicationInfo] = None,
    ):
        """
        Constructor
        """
        dbg._dbg = debug
        self._debug: int = debug
        self.iconName: str = iconName
        self._test = test
        self._splashScreen: Optional[AppSplashScreen] = None
        self._extChangeMode: int = self.EXT_CHANGE_TEST_ON_REQUEST
        self.allowMultipleInstances: bool = False
        self.info: ApplicationInfo = self._getAppInfo(info)
        self.cmdLineArguments: Namespace = self._getCmdLineArguments()
        self.extChangeTimerInterval: int = 60
        self.sharedDataDir: str = ""
        self.privateDataDir: str = ""
        self.globalObjects: List[str] = []
        wx.App.__init__(self, redirect=False, useBestVisual=True)

    def __repr__(self) -> str:
        return '<Application: "%s" by %s>' % (self.AppName, self.VendorName)

    # =========================================================================
    # Private methods
    # =========================================================================

    def _getAppInfo(self, info: Optional[ApplicationInfo] = None) -> ApplicationInfo:
        if isinstance(info, ApplicationInfo):
            return info
        appInfoString = self.getResource("application.yml")
        if isinstance(appInfoString, str):
            return ApplicationInfo.fromString(appInfoString)
        return ApplicationInfo()

    def _getCmdLineArguments(self) -> Namespace:
        """
        :return: parsed command line arguments
        """
        if self.test:
            return Namespace(document=[], disabledPlugins=[])
        # Setup the ArgumentParser
        argumentParser = ArgumentParser(description=self.info.Description)
        argumentParser.add_argument(
            "document",
            type=str,
            nargs="*",
            help="Documents to open",
        )
        argumentParser.add_argument(
            "-x",
            "--eXecute",
            type=str,
            metavar="scriptPath",
            dest="scriptPath",
            help="Execute a script after documents are loaded, if any.",
        )
        argumentParser.add_argument(
            "-s",
            "--noStartupscript",
            action="store_false",
            default=True,
            dest="start_script_exec",
            help="Don't exceute the startup script, even if enabled in the apps preferences.",
        )
        argumentParser.add_argument(
            "-d",
            "--DisablePlugin",
            type=str,
            nargs="*",
            metavar="pluginName",
            dest="disabledPlugins",
            help="Don't load the specified plugins.",
        )
        # return parsed arguments
        return argumentParser.parse_args(sys.argv[1:])

    def _handleCmdLineArguments(self):
        """
        Handle command line arguments
        """
        arguments = self.cmdLineArguments
        config = self.config
        with wx.ConfigPathChanger(config, "/Application/Start/Script/"):
            # execute startup script
            if config.ReadBool("execute", False) and arguments.start_script_exec:
                execfile(config.Read("path", ""))
            # open documents passed as command line arg
            for docPath in arguments.document:
                if os.path.exists(docPath):
                    self.documentManager.CreateDocument(docPath, DOC_SILENT)
            # execute script passed as command line arg
            if arguments.scriptPath:
                execfile(arguments.scriptPath)

    def _initExtChangesTest(self):
        """
        Setup external changes test
        """
        cfg = self.config
        with wx.ConfigPathChanger(cfg, "/Application/ExtChanges/"):
            self.extChangeTimerInterval = cfg.ReadInt(
                "Timer", self.extChangeTimerInterval
            )
            self.extChangeMode = cfg.ReadInt("Mode", self.EXT_CHANGE_TEST_ON_REQUEST)

    def _showSplashScreen(self):
        if self.test:
            return None
        cfg = self.config
        if not cfg.ReadBool("/Application/Start/showSplashScreen", True):
            return None
        spashData = self.getResource("splashscreen.png", "bytes")
        if not isinstance(spashData, bytes):
            return None
        bmp = wx.Image(BytesIO(spashData), wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        if cfg.HasGroup("/Window"):
            with wx.ConfigPathChanger(cfg, "/Window/"):
                if all(
                    (
                        cfg.HasEntry(a)
                        for a in (
                            "x",
                            "y",
                            "width",
                            "height",
                        )
                    )
                ):
                    width = cfg.ReadInt("width", -1)
                    height = cfg.ReadInt("height", -1)
                    x = round(cfg.ReadInt("x", -1) + (width - bmp.Width) / 2)
                    y = round(cfg.ReadInt("y", -1) + (height - bmp.Height) / 2)
                    pos = wx.Point(x, y)
                    # size = wx.Size(cfg.ReadInt("width", -1), cfg.ReadInt("height", -1))
                    splashScreen = AppSplashScreen(
                        bitmap=bmp,
                        splashStyle=SPLASH_NO_TIMEOUT,
                        milliseconds=1000,
                        # parent=None,
                        id=wx.ID_ANY,
                        pos=pos,
                        size=wx.DefaultSize,
                    )
                    splashScreen.SetPosition(pos)
                    return splashScreen
        return AppSplashScreen(
            bmp, SPLASH_CENTER_ON_SCREEN | SPLASH_NO_TIMEOUT, 1000
        )

    def _execFirstRunScript(self):
        """
        Execute firstRun.py when application runns for the first time
        """
        if self.test:
            return
        cfg = self.config
        if cfg.ReadBool("/Application/firstRunDone", False):
            return
        scriptName = "firstRun.py"
        firstRunCode = self.getResource(scriptName)
        if firstRunCode:
            execsource(firstRunCode, scriptName)
        cfg.WriteBool("/Application/firstRunDone", True)

    def _showTipOfTheDay(self):
        """
        Show Tip of the day dialog.
        """
        if self.test:
            return
        cfg = self.config
        with wx.ConfigPathChanger(cfg, "/Application/Start/"):
            showTipOfTheDay = cfg.ReadBool("showTipOfTheDay", True)
            if not showTipOfTheDay:
                return
            currentTip = cfg.ReadInt("currentTipOfTheDay", 0)
            tipProvider = ResourceTipProvider(currentTip)
            if not tipProvider.hasTips:
                return
            showTipOfTheDay = ShowTip(self.TopWindow, tipProvider, showTipOfTheDay)
            cfg.WriteBool("showTipOfTheDay", showTipOfTheDay)
            cfg.WriteBool("currentTipOfTheDay", tipProvider.GetCurrentTip())

    # =========================================================================
    # Public methods
    # =========================================================================

    def OnPreInit(self) -> None:
        wx.App.OnPreInit(self)
        self.globalObjects = [
            "__builtins__",
            "__doc__",
            "__file__",
            "__name__",
            "app",
            "wx",
        ]
        for attr in ("AppName", "AppDisplayName", "VendorName", "VendorDisplayName"):
            setattr(self, attr, getattr(self.info, attr))
        self.Traits.StandardPaths.UseAppInfo(AppInfo_VendorName | AppInfo_AppName)
        if self.test:
            self.config = wx.FileConfig()
        else:
            self.config = self.Traits.CreateConfig()
        self.instanceChecker = wx.SingleInstanceChecker(
            f"{self.AppName}-{wx.GetUserId()}"
        )
        wx.ArtProvider.Push(Artprovider())
        self.extChangeTimer = ExtChangeTestTimer()
        self.listenAndLoadTimer = ListenAndLoadTimer()
        if self.test or (hasattr(sys, "frozen") and sys.frozen):
            self.SetAssertMode(wx.APP_ASSERT_SUPPRESS)

    def OnInit(self) -> bool:
        self.prepareSingleInstanceConfig()
        self._splashScreen = self._showSplashScreen()
        self._pluginManager: PluginManager = self.pluginManagerClass()
        self.prepareSharedDataFolder()
        self.preparePrivateDataFolder()
        self._execFirstRunScript()
        self.SetTopWindow(self.topWindowClass(self.iconName))
        self.RunPostInitQueue()
        self._initExtChangesTest()
        return True

    def OnRun(self) -> int:
        """
        Run the application

            - Show the main application window
            - handle command line arguments
            - close the splash screen
            - show tip of the day
            - enter the main application event loop

        :return: Return code
        """
        self.TopWindow.Show(True)
        self._handleCmdLineArguments()
        if self._splashScreen:
            self._splashScreen.Hide()
            self._splashScreen.Destroy()
            self._splashScreen = None
        shortcutsFromConfig()
        self._showTipOfTheDay()
        main = sys.modules.get("__main__")
        if "main" in main.__dict__:
            del main.__dict__["main"]
        return super().OnRun()

    def run(self) -> int:
        """
        Start the application by calling :meth:`OnRun`

        :return: Return code
        """
        return self.OnRun()

    def splashMessage(self, text: str) -> None:
        """
        Show progress message on splash screen during initialization
        of the application.

        :param text: The message
        """
        if self._splashScreen:
            self._splashScreen.setMessage(text)

    @property
    def test(self) -> bool:
        """
        Turns the application in test mode. This disables the splash screen
        and doesn't create directories, files or registry entries

        :return: Test mode enabled
        """
        return self._test

    @property
    def extChangeMode(self) -> int:
        """
        Mode how external changes of documents should be checked.

        May be one of:
            - EXT_CHANGE_TEST_ON_REQUEST
            - EXT_CHANGE_TEST_ON_ACTIVATE
            - EXT_CHANGE_TEST_ON_TIMER

        :return: current mode
        """
        return self._extChangeMode

    @extChangeMode.setter
    def extChangeMode(self, value: int):
        assert value in (
            self.EXT_CHANGE_TEST_ON_REQUEST,
            self.EXT_CHANGE_TEST_ON_ACTIVATE,
            self.EXT_CHANGE_TEST_ON_TIMER,
        )
        if value != self._extChangeMode:
            if self._extChangeMode == self.EXT_CHANGE_TEST_ON_ACTIVATE:
                self.Unbind(wx.EVT_ACTIVATE_APP, handler=self.on_ACTIVATE_APP)
            elif self._extChangeMode == self.EXT_CHANGE_TEST_ON_TIMER:
                self.extChangeTimer.Stop()
            if value == self.EXT_CHANGE_TEST_ON_ACTIVATE:
                self.Bind(wx.EVT_ACTIVATE_APP, self.on_ACTIVATE_APP)
            elif value == self.EXT_CHANGE_TEST_ON_TIMER:
                self.extChangeTimer.Start(self.extChangeTimerInterval * 1000)
            self._extChangeMode = value

    @property
    def pluginManager(self) -> PluginManager:
        """The plugin manager of the running application"""
        return self._pluginManager

    @property
    def panelManager(self) -> PanelManager:
        """The panel manager of the running application"""
        return self.TopWindow.panelManager

    @property
    def documentManager(self) -> DocumentManager:
        """The document manager of the running application"""
        return self.TopWindow.documentManager

    @property
    def version(self) -> str:
        """
        :return: The version string of the running application.
        """
        module = self.__class__.__module__
        if module == "__main__":
            try:
                return inspect.getmodule(self.__class__).__version__
            except AttributeError:
                return "0.0.0"
        try:
            return metadata.version(module)
        except metadata.PackageNotFoundError:
            return "0.0.0"

    def getResource(self, name: str, type: str = "str") -> Optional[Union[str, bytes]]:
        if type not in ("str", "bytes"):
            raise ValueError(
                f"Unknown resource type: '{type}', expected 'str' or 'bytes'"
            )
        module = self.__class__.__module__
        if module == "__main__":
            # we are defined in a simple python script
            resourcePath = os.path.join(
                os.path.dirname(inspect.getfile(self.__class__)), self.resourceContainerName, name
            )
            if os.path.isfile(resourcePath):
                if type == "str":
                    with open(resourcePath, "r", encoding="utf-8") as resourceFile:
                        return resourceFile.read()
                with open(
                    resourcePath,
                    "rb",
                ) as resourceFile:
                    return resourceFile.read()
            log.debug("Resource with name '%s' not found at %s", name, resourcePath)
            return None
        # we are defined in a package
        dataPackage = (
            f"{metadata.PackagePath(module).stem}.{self.resourceContainerName}"
        )
        if sys.version_info < (3, 11):
            try:
                if resources.is_resource(dataPackage, name):
                    if type == "str":
                        return resources.read_text(dataPackage, name)
                    return resources.read_binary(dataPackage, name)
            except ModuleNotFoundError:
                pass
        else:
            try:
                if resources.files(dataPackage).joinpath(name).is_file():
                    if type == "str":
                        return resources.files(dataPackage).joinpath(name).read_text()
                    return resources.files(dataPackage).joinpath(name).read_bytes()
            except ModuleNotFoundError:
                pass

        log.debug("Resource with name '%s' not found in %r", name, dataPackage)
        return None

    def prepareSingleInstanceConfig(self) -> None:
        if self.test:
            return
        self.allowMultipleInstances = self.config.ReadBool(
            "/Application/Start/MultipleInstances", False
        )
        if self.allowMultipleInstances:
            return
        # create shared memory temporary file
        if wx.Platform == "__WXMSW__":
            tfile = tempfile.TemporaryFile(prefix="ag", suffix="tmp")
            fno = tfile.fileno()
            self._sharedMemory = mmap.mmap(fno, 1024, "shared_memory")
        else:
            tfile = open(
                os.path.join(
                    tempfile.gettempdir(),
                    tempfile.gettempprefix()
                    + self.GetAppName()
                    + "-"
                    + wx.GetUserId()
                    + "AGSharedMemory",
                ),
                "w+b",
            )
            tfile.write(b"*")  # available buffer
            tfile.seek(1024)
            tfile.write(b" ")
            tfile.flush()
            fno = tfile.fileno()
            self._sharedMemory = mmap.mmap(fno, 1024)
        if self.instanceChecker.IsAnotherRunning():
            if self.cmdLineArguments.document:
                data = pickle.dumps(self.cmdLineArguments.document)
                sharedMemory = self._sharedMemory
                while True:
                    sharedMemory.seek(0)
                    marker = sharedMemory.read_byte()
                    if marker == 0 or chr(marker) == "*":  # available buffer
                        sharedMemory.seek(0)
                        # set writing marker
                        sharedMemory.write_byte(ord("-"))
                        # write files we tried to open to shared memory
                        sharedMemory.write(data)
                        sharedMemory.seek(0)
                        sharedMemory.write_byte(ord("+"))  # set finished writing marker
                        sharedMemory.flush()
                        break
                    else:
                        time.sleep(1)  # give enough time for buffer to be available
            sys.exit(0)
        else:
            self.listenAndLoadTimer.Start(250)

    def prepareSharedDataFolder(self) -> None:
        self.splashMessage("Preparing shared data folder")
        cfg = self.config
        defaultFolder = os.path.join(
            self.Traits.StandardPaths.UserLocalDataDir, "shared"
        )
        with wx.ConfigPathChanger(cfg, "/Application/SharedData/"):
            folder = cfg.Read("Dir", defaultFolder)
            url = cfg.Read("URL", "")
            pull_on_start = cfg.ReadBool("PullOnStart", False)
        if folder:
            if not os.path.isdir(folder) and not self.test:
                try:
                    os.makedirs(folder)
                except PermissionError:
                    folder = ""
            self.sharedDataDir = folder
        if has_git and url and folder:
            try:
                repo = Repo(folder)
            except InvalidGitRepositoryError:
                repo = Repo.init(folder)
            if not repo.remotes:
                remote = repo.create_remote("origin", url)
            else:
                try:
                    remote = repo.remote(name="origin")
                except ValueError:
                    remote = repo.create_remote("origin", url)
            urls = [u for u in remote.urls]
            old_url = None
            if url not in urls:
                if len(urls) == 1:
                    old_url = urls[0]
                remote.set_url(url, old_url)
            if pull_on_start:
                self.splashMessage("Pulling shared data")
                self.pullSharedData()

    def pullSharedData(self) -> None:
        if self.test:
            return
        if has_git:
            if self.sharedDataDir:
                try:
                    repo = Repo(self.sharedDataDir)
                except InvalidGitRepositoryError:
                    wx.LogError(f"{self.sharedDataDir} is not a valid GIT repo")
                    return
                try:
                    remote = repo.remote(name="origin")
                except ValueError:
                    wx.LogError(f"{self.sharedDataDir} has no valid remote 'origin'")
                    return
                try:
                    remote.pull("master")
                    wx.LogStatus(f"{remote} pulled")
                except GitCommandError as e:
                    wx.LogError(f"{e}")
        else:
            wx.LogWarning(" GIT not available\n\nShared Data will not be pulled!")

    def preparePrivateDataFolder(self) -> None:
        self.splashMessage("Preparing private data folder")
        cfg = self.config
        defaultFolder = os.path.join(
            self.Traits.StandardPaths.UserLocalDataDir, "private"
        )
        with wx.ConfigPathChanger(cfg, "/Application/PrivateData/"):
            folder = cfg.Read("Dir", defaultFolder)
        if not os.path.isdir(folder) and not self.test:
            os.makedirs(folder)
        self.privateDataDir = folder

    def MacOpenFiles(self, fileNames) -> None:
        for filename in fileNames:
            self.documentManager.CreateDocument(filename, DOC_SILENT)

    # def MacNewFile(self):
    #     docManager = self.documentManager
    #     if docManager:
    #         docManager.CreateDocument(None, DOC_NEW)

    def AddPostInitAction(self, action: FunctionType) -> None:
        """
        Add actions to the post init queue.

        This is intended for plug-in initialization which require an existing
        application window.

        Args:
            action (function): Function which takes the app instance as paramerter
                when called by `App.RunPostInitQueue`
        """
        self._post_init_queue.append(action)

    def RunPostInitQueue(self) -> None:
        """
        Execute the queued post init actions
        """
        while self._post_init_queue:
            action = self._post_init_queue.pop(0)
            try:
                action(self)
            except:
                log.exception(
                    "Can't execute post init action '%s' from module '%s'",
                    action.__name__,
                    action.__module__,
                )

    # =========================================================================
    # Event Handler
    # =========================================================================

    def on_ACTIVATE_APP(self, event) -> None:
        if event.Active:
            self.documentManager.testForExternalChanges(testAll=True)
