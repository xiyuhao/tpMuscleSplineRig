#! /usr/bin/python

"""
    File name: tpMusclSplineRig.py
    Author: Tomas Poveda - www.cgart3d.com
    Description: Tool to create MuscleSpline setups quickly
"""

try:
    from PySide2.QtGui import *
    from PySide2.QtCore import *
    from PySide2.QtWidgets import *
    from shiboken2 import wrapInstance
except:
    from PySide.QtGui import *
    from PySide.QtCore import *
    from shiboken import wrapInstance

import maya.OpenMayaUI as OpenMayaUI
import pymel.core as pm
import maya.cmds as cmds

# -------------------------------------------------------------------------------------------------

def _getMayaWindow():
    """
    Return the Maya main window widget as a Python object
    :return: Maya Window
    """

    ptr = OpenMayaUI.MQtUtil.mainWindow()
    if ptr is not None:
        return wrapInstance(long(ptr), QMainWindow)


def tpUndo(fn):
    """
    Simple undo wrapper. Use @tpUndo above the function to wrap it.
    @param fn: function to wrap
    @return wrapped function
    """

    def wrapper(*args, **kwargs):
        cmds.undoInfo(openChunk=True)
        try:
            ret = fn(*args, **kwargs)
        finally:
            cmds.undoInfo(closeChunk=True)
        return ret

    return wrapper


def snap(source=None, target=None):
    """
    Snaps (only translation) one object (target) to another (source)
    """

    if source is None and target is None:
        sel = pm.ls(selection=True)
        if len(sel) >= 2:
            source = sel[0]
            target = sel[1]
        else:
            pm.error('tpRigLib: No objects to snap selected')
    else:
        pos = pm.xform(target, query=True, worldSpace=True, translation=True)
        rpA = pm.xform(target, query=True, rp=True)
        rpB = pm.xform(source, query=True, rp=True)

        pm.xform(source, translation=(pos[0] + rpA[0] - rpB[0], pos[1] + rpA[1] - rpB[1], pos[2] + rpA[2] - rpB[2]),
                 worldSpace=True)

        pm.select(source)


def matchTransforms(source, target):
    """
    Match transform of one object (target) to another (source)
    """

    pm.delete(pm.parentConstraint(target, source, weight=1, mo=False))


# -------------------------------------------------------------------------------------------------

class tpSplitter(QWidget, object):
    def __init__(self, text=None, shadow=True, color=(150, 150, 150)):

        """
        Basic standard splitter with optional text
        :param str text: Optional text to include as title in the splitter
        :param bool shadow: True if you want a shadow above the splitter
        :param tuple(int) color: Color of the slitter's text
        """

        super(tpSplitter, self).__init__()

        self.setMinimumHeight(2)
        self.setLayout(QHBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)
        self.layout().setAlignment(Qt.AlignVCenter)

        firstLine = QFrame()
        firstLine.setFrameStyle(QFrame.HLine)
        self.layout().addWidget(firstLine)

        mainColor = 'rgba(%s, %s, %s, 255)' % color
        shadowColor = 'rgba(45, 45, 45, 255)'

        bottomBorder = ''
        if shadow:
            bottomBorder = 'border-bottom:1px solid %s;' % shadowColor

        styleSheet = "border:0px solid rgba(0,0,0,0); \
                      background-color: %s; \
                      max-height: 1px; \
                      %s" % (mainColor, bottomBorder)

        firstLine.setStyleSheet(styleSheet)

        if text is None:
            return

        firstLine.setMaximumWidth(5)

        font = QFont()
        font.setBold(True)

        textWidth = QFontMetrics(font)
        width = textWidth.width(text) + 6

        label = QLabel()
        label.setText(text)
        label.setFont(font)
        label.setMaximumWidth(width)
        label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)

        self.layout().addWidget(label)

        secondLine = QFrame()
        secondLine.setFrameStyle(QFrame.HLine)
        secondLine.setStyleSheet(styleSheet)

        self.layout().addWidget(secondLine)


class tpSplitterLayout(QHBoxLayout, object):
    def __init__(self):
        """
        Basic splitter to separate layouts
        """

        super(tpSplitterLayout, self).__init__()

        self.setContentsMargins(40, 2, 40, 2)

        splitter = tpSplitter(shadow=False, color=(60, 60, 60))
        splitter.setFixedHeight(2)

        self.addWidget(splitter)


# -------------------------------------------------------------------------------------------------

class tpMuscleSplineRigWin(QDialog, object):
    def __init__(self):
        super(tpMuscleSplineRigWin, self).__init__(_getMayaWindow())

        winName = 'tpMuscleSplineRigDialog'

        # Check if this UI is already open. If it is then delete it before  creating it anew
        if cmds.window(winName, exists=True):
            cmds.deleteUI(winName, window=True)
        elif cmds.windowPref(winName, exists=True):
            cmds.windowPref(winName, remove=True)

        # Set the dialog object name, window title and size
        self.setObjectName(winName)
        self.setWindowTitle('tpMuscleSplineRig')
        self.setFixedSize(QSize(330, 480))

        self.customUI()

    def customUI(self):

        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)
        mainLayout.setContentsMargins(5, 5, 5, 5)
        mainLayout.setSpacing(2)
        mainLayout.setAlignment(Qt.AlignTop)

        mainLayout.addLayout(tpSplitterLayout())

        mainLayout.addWidget(tpSplitter('MUSCLE SETUP'))

        muscleSetupWidget = QWidget()
        widgetPalette = QPalette()
        widgetPalette.setColor(QPalette.Background, QColor.fromRgb(55, 55, 55))
        muscleSetupWidget.setAutoFillBackground(True)
        muscleSetupWidget.setPalette(widgetPalette)
        muscleSetupLayout = QVBoxLayout()
        muscleSetupLayout.setContentsMargins(0, 0, 0, 0)
        muscleSetupLayout.setSpacing(0)
        muscleSetupWidget.setLayout(muscleSetupLayout)
        mainLayout.addWidget(muscleSetupWidget)

        nameLayout = QHBoxLayout()
        nameLayout.setContentsMargins(0, 0, 10, 0)
        nameLayout.setAlignment(Qt.AlignLeft)
        muscleSetupLayout.addLayout(nameLayout)
        nameLbl = QLabel('                 Name: ')
        self.nameLine = QLineEdit()
        self.nameLine.setText('Char01_Spine')
        nameLayout.addWidget(nameLbl)
        nameLayout.addWidget(self.nameLine)
        mainLayout.addLayout(nameLayout)

        charSizeLayout = QHBoxLayout()
        charSizeLayout.setContentsMargins(0, 0, 10, 0)
        charSizeLayout.setAlignment(Qt.AlignLeft)
        muscleSetupLayout.addLayout(charSizeLayout)
        charSizeLbl = QLabel('                    Size: ')
        self.charSizeSpn = QDoubleSpinBox()
        self.charSizeSpn.setMinimum(1.0)
        self.charSizeSpn.setValue(1.0)
        charSizeLayout.addWidget(charSizeLbl)
        charSizeLayout.addWidget(self.charSizeSpn)

        muscleSetupLayout.addLayout(tpSplitterLayout())

        insertionCtrlsLayout = QHBoxLayout()
        insertionCtrlsLayout.setContentsMargins(0, 0, 10, 0)
        muscleSetupLayout.addLayout(insertionCtrlsLayout)
        insertionNumLayout = QHBoxLayout()
        insertionNumLayout.setAlignment(Qt.AlignLeft)
        insertionNumLayout.setSpacing(5)
        insretionCtrlsLbl = QLabel('Num Insertion Controls: ')
        self.insertionCtrlsSpn = QSpinBox()
        self.insertionCtrlsSpn.setMinimum(2)
        self.insertionCtrlsSpn.setValue(3)
        self.insertionCtrlsSpn.setMaximum(24)
        insertionNumLayout.addWidget(insretionCtrlsLbl)
        insertionNumLayout.addWidget(self.insertionCtrlsSpn)
        insertionTypeLayout = QHBoxLayout()
        insertionTypeLayout.setAlignment(Qt.AlignRight)
        insertionTypeLayout.setSpacing(5)
        insertionTypeLbl = QLabel('Type: ')
        self.insertionTypeCbx = QComboBox()
        for ctrlType in ['cube', 'circleY', 'null']:
            self.insertionTypeCbx.addItem(ctrlType)
        insertionTypeLayout.addWidget(insertionTypeLbl)
        insertionTypeLayout.addWidget(self.insertionTypeCbx)
        insertionCtrlsLayout.addLayout(insertionNumLayout)
        insertionCtrlsLayout.addLayout(insertionTypeLayout)

        numDrivenJntsLayout = QHBoxLayout()
        numDrivenJntsLayout.setContentsMargins(0, 0, 10, 0)
        muscleSetupLayout.addLayout(numDrivenJntsLayout)
        numDrivenLayout = QHBoxLayout()
        numDrivenLayout.setAlignment(Qt.AlignLeft)
        numDrivenLayout.setSpacing(5)
        numDrivenLbl = QLabel('                    Num Driven: ')
        self.numDrivenSpn = QSpinBox()
        self.numDrivenSpn.setMinimum(1)
        self.numDrivenSpn.setValue(5)
        self.numDrivenSpn.setMaximum(64)
        numDrivenLayout.addWidget(numDrivenLbl)
        numDrivenLayout.addWidget(self.numDrivenSpn)

        numDrivenTypeLayout = QHBoxLayout()
        numDrivenTypeLayout.setAlignment(Qt.AlignRight)
        numDrivenTypeLayout.setSpacing(5)
        numDrivenTypeLbl = QLabel('Type: ')
        self.numDrivenTypeCbx = QComboBox()
        for ctrlType in ['joint', 'circleY', 'null']:
            self.numDrivenTypeCbx.addItem(ctrlType)
        numDrivenTypeLayout.addWidget(numDrivenTypeLbl)
        numDrivenTypeLayout.addWidget(self.numDrivenTypeCbx)

        numDrivenJntsLayout.addLayout(numDrivenLayout)
        numDrivenJntsLayout.addLayout(numDrivenTypeLayout)

        muscleSetupLayout.addLayout(tpSplitterLayout())

        extraOptionsLayout = QHBoxLayout()
        extraOptionsLayout.setContentsMargins(5, 5, 5, 5)
        extraOptionsLayout.setSpacing(10)
        extraOptionsLayout.setAlignment(Qt.AlignCenter)
        muscleSetupLayout.addLayout(extraOptionsLayout)
        self.cnsMidCtrlsCbx = QCheckBox('Constrain Mid Controls')
        self.lockCtrlsScaleCbx = QCheckBox('Lock Controls Scale')
        self.lockCtrlsScaleCbx.setChecked(True)
        extraOptionsLayout.addWidget(self.cnsMidCtrlsCbx)
        extraOptionsLayout.addWidget(self.lockCtrlsScaleCbx)

        mainLayout.addLayout(tpSplitterLayout())

        mainLayout.addWidget(tpSplitter('ADVANCED SETUP'))

        self.enableCbx = QCheckBox('Enable')
        mainLayout.addWidget(self.enableCbx)

        advancedLayout = QVBoxLayout()
        advancedLayout.setContentsMargins(0, 0, 0, 0)
        advancedLayout.setSpacing(0)
        self.advancedWidget = QWidget()
        self.advancedWidget.setEnabled(False)
        self.advancedWidget.setLayout(advancedLayout)
        mainLayout.addWidget(self.advancedWidget)

        ctrlSuffixLayout = QHBoxLayout()
        ctrlSuffixLbl = QLabel('               Control Suffix: ')
        self.ctrlSuffixLine = QLineEdit()
        self.ctrlSuffixLine.setText('ctrl')
        ctrlSuffixLayout.addWidget(ctrlSuffixLbl)
        ctrlSuffixLayout.addWidget(self.ctrlSuffixLine)

        jointSuffixLayout = QHBoxLayout()
        jointSuffixLbl = QLabel('                    Joint Suffix: ')
        self.jointSuffixLine = QLineEdit()
        self.jointSuffixLine.setText('jnt')
        jointSuffixLayout.addWidget(jointSuffixLbl)
        jointSuffixLayout.addWidget(self.jointSuffixLine)

        grpSuffixLayout = QHBoxLayout()
        grpSuffixLbl = QLabel('                 Group Suffix: ')
        self.grpSuffixLine = QLineEdit()
        self.grpSuffixLine.setText('grp')
        grpSuffixLayout.addWidget(grpSuffixLbl)
        grpSuffixLayout.addWidget(self.grpSuffixLine)

        drvSuffixLayout = QHBoxLayout()
        drvSuffixLbl = QLabel('                 Driven Suffix: ')
        self.drvSuffixLine = QLineEdit()
        self.drvSuffixLine.setText('drv')
        drvSuffixLayout.addWidget(drvSuffixLbl)
        drvSuffixLayout.addWidget(self.drvSuffixLine)

        for layout in [ctrlSuffixLayout, jointSuffixLayout, grpSuffixLayout, drvSuffixLayout]:
            advancedLayout.addLayout(layout)

        advancedLayout.addLayout(tpSplitterLayout())

        muscleSetLayout = QHBoxLayout()
        advancedLayout.addLayout(muscleSetLayout)
        muscleSetLbl = QLabel('Main Muscle Set Name: ')
        self.mainSetLine = QLineEdit()
        self.mainSetLine.setText('setMUSCLERIGS')
        muscleSetLayout.addWidget(muscleSetLbl)
        muscleSetLayout.addWidget(self.mainSetLine)

        setSuffixLayout = QHBoxLayout()
        advancedLayout.addLayout(setSuffixLayout)
        setSuffixLbl = QLabel('          Muscle Set Suffix: ')
        self.setSuffixLine = QLineEdit()
        self.setSuffixLine.setText('RIG')
        setSuffixLayout.addWidget(setSuffixLbl)
        setSuffixLayout.addWidget(self.setSuffixLine)

        muscleSplineNameLayout = QHBoxLayout()
        advancedLayout.addLayout(muscleSplineNameLayout)
        muscleSplineNameLbl = QLabel('    Muscle Spline Name: ')
        self.muscleSplineNameLine = QLineEdit()
        self.muscleSplineNameLine.setText('tpMuscleSpline')
        muscleSplineNameLayout.addWidget(muscleSplineNameLbl)
        muscleSplineNameLayout.addWidget(self.muscleSplineNameLine)

        controlsGroupSuffixLayout = QHBoxLayout()
        advancedLayout.addLayout(controlsGroupSuffixLayout)
        controlsGroupSuffixLbl = QLabel(' Controls Group Suffix: ')
        self.controlsGroupSuffixLine = QLineEdit()
        self.controlsGroupSuffixLine.setText('ctrls')
        controlsGroupSuffixLayout.addWidget(controlsGroupSuffixLbl)
        controlsGroupSuffixLayout.addWidget(self.controlsGroupSuffixLine)

        jointsGroupSuffixLayout = QHBoxLayout()
        advancedLayout.addLayout(jointsGroupSuffixLayout)
        jointsGroupSuffixLbl = QLabel('      Joints Group Suffix: ')
        self.jointsGroupSuffixLine = QLineEdit()
        self.jointsGroupSuffixLine.setText('joints')
        jointsGroupSuffixLayout.addWidget(jointsGroupSuffixLbl)
        jointsGroupSuffixLayout.addWidget(self.jointsGroupSuffixLine)

        rootSuffixLayout = QHBoxLayout()
        advancedLayout.addLayout(rootSuffixLayout)
        rootSuffixLbl = QLabel('        Root Group Suffix: ')
        self.rootSuffixLine = QLineEdit()
        self.rootSuffixLine.setText('root')
        rootSuffixLayout.addWidget(rootSuffixLbl)
        rootSuffixLayout.addWidget(self.rootSuffixLine)

        autoSuffixLayout = QHBoxLayout()
        advancedLayout.addLayout(autoSuffixLayout)
        autoSuffixLbl = QLabel('        Auto Group Suffix: ')
        self.autoSuffixLine = QLineEdit()
        self.autoSuffixLine.setText('auto')
        autoSuffixLayout.addWidget(autoSuffixLbl)
        autoSuffixLayout.addWidget(self.autoSuffixLine)

        mainLayout.addLayout(tpSplitterLayout())

        self.createMuscleSplineRigBtn = QPushButton('Create Muscle Spline Rig')
        mainLayout.addWidget(self.createMuscleSplineRigBtn)

        mainLayout.addLayout(tpSplitterLayout())

        # footerLayout = QHBoxLayout()
        # mainLayout.addLayout(footerLayout)
        # cgart3dBtn = QPushButton('Tomas Poveda - www.cgart3d.com')
        # cgart3dBtn.setStyleSheet('text-align:right;')
        # cgart3dBtn.setMaximumHeight(15)
        # footerLayout.addWidget(cgart3dBtn)

        # === SIGNALS === #
        self.createMuscleSplineRigBtn.clicked.connect(self._createMuscleSpline)
        self.nameLine.textChanged.connect(self.checkUIState)
        self.enableCbx.toggled.connect(self.checkUIState)

    def checkUIState(self):
        self.createMuscleSplineRigBtn.setEnabled(not self.nameLine.text() == '')
        self.advancedWidget.setEnabled(self.enableCbx.isChecked())

    def _createMuscleSpline(self):

        name = self.nameLine.text()
        suffixCtrl = self.ctrlSuffixLine.text()
        suffixJnt = self.jointSuffixLine.text()
        suffixGrp = self.grpSuffixLine.text()
        suffixDrv = self.drvSuffixLine.text()
        charSize = self.charSizeSpn.value()
        numControls = self.insertionCtrlsSpn.value()
        controlType = self.insertionTypeCbx.currentText()
        numDrivens = self.numDrivenSpn.value()
        drivenType = self.numDrivenTypeCbx.currentText()
        constrainMid = self.cnsMidCtrlsCbx.isChecked()
        controlsGrpSuffix = self.controlsGroupSuffixLine.text()
        jointsGrpSuffix = self.jointsGroupSuffixLine.text()
        rootSuffix = self.rootSuffixLine.text()
        autoSuffix = self.autoSuffixLine.text()

        mainSetName = self.mainSetLine.text()
        rigSetSuffix = self.setSuffixLine.text()
        muscleSplineName = self.muscleSplineNameLine.text()

        return tpMuscleSplineRig(name=name,
                        suffixCtrl=suffixCtrl, suffixJnt=suffixJnt, suffixGrp=suffixGrp, suffixDrv=suffixDrv,
                        charSize=charSize,
                        numControls=numControls, controlType=controlType,
                        numDrivens=numDrivens, drivenType=drivenType,
                        constrainMid=constrainMid,
                        mainSetName=mainSetName,
                        rigSetSuffix=rigSetSuffix,
                        muscleSplineName=muscleSplineName,
                        controlsGrpSuffix=controlsGrpSuffix, jointsGrpSuffix=jointsGrpSuffix,
                        rootSuffix=rootSuffix, autoSuffix=autoSuffix,
                        lockScale=self.lockCtrlsScaleCbx.isChecked(), lockJiggleAttributes=False
                        )

class tpMuscleSplineCtrl(object):
    def __init__(self, ctrlName, ctrlType, charSize):

        self._ctrl = None
        self._root = None
        self._auto = None

        if ctrlType == 'cube':
            ctrlDefSize = 0.25 * charSize
            self._ctrl = pm.curve(name=ctrlName, degree=1,
                            point=[(-ctrlDefSize, ctrlDefSize, ctrlDefSize), (ctrlDefSize, ctrlDefSize, ctrlDefSize),
                                   (ctrlDefSize, ctrlDefSize, -ctrlDefSize), (-ctrlDefSize, ctrlDefSize, -ctrlDefSize),
                                   (-ctrlDefSize, ctrlDefSize, ctrlDefSize), (-ctrlDefSize, -ctrlDefSize, ctrlDefSize),
                                   (-ctrlDefSize, -ctrlDefSize, -ctrlDefSize),(ctrlDefSize, -ctrlDefSize, -ctrlDefSize), (ctrlDefSize, -ctrlDefSize, ctrlDefSize),
                                   (-ctrlDefSize, -ctrlDefSize, ctrlDefSize), (ctrlDefSize, -ctrlDefSize, ctrlDefSize),
                                   (ctrlDefSize, ctrlDefSize, ctrlDefSize), (ctrlDefSize, ctrlDefSize, -ctrlDefSize),
                                   (ctrlDefSize, -ctrlDefSize, -ctrlDefSize),
                                   (-ctrlDefSize, -ctrlDefSize, -ctrlDefSize),
                                   (-ctrlDefSize, ctrlDefSize, -ctrlDefSize)], knot=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])
        elif ctrlType == 'circleY':
            self._ctrl = pm.circle(name=ctrlName, degree=3, center=[0, 0, 0], normal=[0, 1, 0], sweep=360,
                             radius=0.25 * charSize, useTolerance=False, sections=8, constructionHistory=False)[0]
        elif ctrlType == 'null':
            self._ctrl = pm.group(name=ctrlName, empty=True, world=True)

    @property
    def control(self):
        return self._ctrl

    @property
    def root(self):
        return self._root

    @property
    def auto(self):
        return self._auto

    @root.setter
    def root(self, newRoot):
        self._root = newRoot

    @auto.setter
    def auto(self, newAuto):
        self._auto = newAuto

class tpMuscleSplineRig(object):
    def __init__(
            self,
            name,
            suffixCtrl='ctrl', suffixJnt='jnt', suffixGrp='grp', suffixDrv='drv',
            charSize=1.0,
            numControls=3, controlType='cube',
            numDrivens=5, drivenType='joint',
            constrainMid=False,
            mainSetName='setMUSCLERIGS',
            rigSetSuffix='RIG',
            muscleSplineName='tpMuscleSpline',
            controlsGrpSuffix='controls', jointsGrpSuffix='joints',
            rootSuffix='root', autoSuffix='auto',
            lockScale=True, lockJiggleAttributes=False):

        self.makeSpline(
            name=name,
            suffixCtrl=suffixCtrl, suffixJnt=suffixJnt, suffixGrp=suffixGrp, suffixDrv=suffixDrv,
            charSize=charSize,
            numControls=numControls, controlType=controlType,
            numDrivens=numDrivens, drivenType=drivenType,
            constrainMid=constrainMid,
            mainSetName=mainSetName,
            rigSetSuffix=rigSetSuffix,
            muscleSplineName=muscleSplineName,
            controlsGrpSuffix=controlsGrpSuffix, jointsGrpSuffix=jointsGrpSuffix,
            rootSuffix=rootSuffix, autoSuffix=autoSuffix,
            lockScale=lockScale, lockJiggleAttributes=lockJiggleAttributes
        )

    @tpUndo
    def makeSpline(self,
                   name,
                   suffixCtrl='ctrl', suffixJnt='jnt', suffixGrp='grp', suffixDrv='drv',
                   charSize=1.0,
                   numControls=3, controlType='cube',
                   numDrivens=5, drivenType='joint',
                   constrainMid=False,
                   mainSetName='setMUSCLERIGS',
                   rigSetSuffix='RIG',
                   muscleSplineName='tpMuscleSpline',
                   controlsGrpSuffix='controls', jointsGrpSuffix='joints',
                   rootSuffix='root', autoSuffix='auto',
                   lockScale=True, lockJiggleAttributes=False
                   ):

        """
        Makes a muscle spline rig
        :param str prefix: Prefix for the muscle setup
        :param str name: Name for the muscle setup
        :param str suffixCtrl: Suffix for controls objects of the muscle setup
        :param str suffixJnt: Suffix for joints objects of the muscle setup
        :param int numControls: Number of controls for the muscle rig setup
        :param float charSize: Number that controls the global scale of the muscle setup
        :param int numControls: Number of control curves for the muscle setup
        :param str controlType: Name of the control type we want to use for the controls (cube, circleY, null)
        :param int numDrivens: Number of deformations joints for the muscle setup
        :param str drivenType: Name of the control type we want to use for the controls (cube, circleY, null)
        :param bool constrainMid: True if you want to constraint the mid control to the start and end controls
        :return: None
        """
        
        test = pm.pluginInfo('MayaMuscle.mll', query=True, loaded=True)
        if not pm.pluginInfo('MayaMuscle.mll', query=True, loaded=True):
            print 'Maya Muscle plugin is not loaded. Trying to load ...'
            try:
                pm.loadPlugin('MayaMuscle.mll')
            except:
                pm.error('Impossible to load Maya Muscle plugin ...')
                return
            
        baseName = name

        if not pm.objExists(mainSetName):
            pm.sets(name=mainSetName, empty=True)

        setRig = 'set' + baseName + rigSetSuffix
        if not pm.objExists(setRig):
            pm.sets(name=setRig, empty=True)
            pm.sets(setRig, include=mainSetName)

        if pm.objExists(muscleSplineName + '_' + baseName) or pm.objExists(
                                                baseName + '_' + muscleSplineName + '_' + suffixGrp):
            msgBox = QMessageBox()
            msgBox.setWindowTitle('Muscle/Spline Already Exists')
            msgBox.setText(
                'A Muscle or Spline with the given name "Spline" already exists.\nPlease choose a different name.')
            msgBox.exec_()
            pm.error('Muscle spline {0} already exists'.format(baseName + '_' + muscleSplineName))
            return False

        # Make main group
        self.mainGrp = pm.group(name=baseName + '_' + muscleSplineName + '_' + suffixGrp, empty=True, world=True)
        pm.sets(setRig, include=self.mainGrp)

        # Create spline node
        self.splineNode = pm.createNode('cMuscleSpline', name=baseName + '_' + muscleSplineName + 'Shape')
        self.splineNodeXForm = pm.rename(pm.listRelatives(self.splineNode, parent=True, type='transform'),
                                    baseName + '_' + muscleSplineName)
        self.splineNodeXForm.inheritsTransform.set(False)
        pm.parent(self.splineNodeXForm, self.mainGrp)
        for attr in ['DISPLAY', 'TANGENTS', 'LENGTH']:
            pm.setAttr(self.splineNode + '.' + attr, lock=True)
        for xform in ['t', 'r', 's']:
            for axis in ['x', 'y', 'z']:
                pm.setAttr(self.splineNodeXForm + '.' + xform + axis, lock=True, keyable=False)
        pm.connectAttr("time1.outTime", self.splineNode + '.inTime', force=True)
        pm.sets(setRig, include=self.splineNode)

        # Make some interesting attributes of the cMuscleSpline node available to the user through channel box
        pm.addAttr(self.splineNode, longName='curLen', keyable=True)
        pm.addAttr(self.splineNode, longName='pctSquash', keyable=True)
        pm.addAttr(self.splineNode, longName='pctStretch', keyable=True)
        self.splineNode.curLen.connect(self.splineNode.outLen)
        self.splineNode.pctSquash.connect(self.splineNode.outPctSquash)
        self.splineNode.pctStretch.connect(self.splineNode.outPctStretch)

        # Create group for the controls
        self.controlsGrp = pm.group(name=baseName + '_' + muscleSplineName + '_' + controlsGrpSuffix, empty=True, world=True)
        self.controlsGrp.inheritsTransform.set(True)
        pm.parent(self.controlsGrp, self.mainGrp)
        for xform in ['t', 'r', 's']:
            for axis in ['x', 'y', 'z']:
                pm.setAttr(self.controlsGrp + '.' + xform + axis, lock=True, keyable=False)
        pm.sets(setRig, include=self.controlsGrp)

        # Create drivens group
        self.drivensGrp = pm.group(name=baseName + '_' + muscleSplineName + '_' + jointsGrpSuffix, empty=True, world=True)
        self.drivensGrp.inheritsTransform.set(False)
        pm.parent(self.drivensGrp, self.mainGrp)
        for xform in ['t', 'r', 's']:
            for axis in ['x', 'y', 'z']:
                pm.setAttr(self.drivensGrp + '.' + xform + axis, lock=True, keyable=False)
        pm.sets(setRig, include=self.drivensGrp)

        # Create controls
        self.controls = []
        self.consGrps = []
        self.rootGrps = []
        for i in range(numControls):
            ctrlName = baseName + '_' + muscleSplineName + '_' + str(i) + '_' + suffixCtrl
            ctrl = tpMuscleSplineCtrl(ctrlName, controlType, charSize)
            self.controls.append(ctrl)

            # Create root and auto groups
            rootGrp = pm.group(name=ctrlName.replace(suffixCtrl, rootSuffix), empty=True, world=True)
            consGrp = pm.group(name=ctrlName.replace(suffixCtrl, autoSuffix), empty=True, world=True)
            self.rootGrps.append(rootGrp)
            self.consGrps.append(consGrp)
            ctrl.root = rootGrp
            ctrl.auto = consGrp

            # Place the controls and its groups vertically on the Y axis
            for toTransform in [ctrl.control, rootGrp, consGrp]:
                pm.xform(toTransform, translation=(0, i * charSize, 0), absolute=True, worldSpace=True)

            # Parent all the controls
            pm.parent(ctrl.control, consGrp)
            pm.parent(consGrp, rootGrp)
            pm.parent(rootGrp, self.controlsGrp)

            # Color the controls
            if ctrl.control.getShape() is not None:
                ctrl.control.getShape().overrideEnabled.set(True)
                ctrl.control.getShape().overrideColor.set(17)

            # Make middle controls jiggle by default
            jiggle = 1.0
            if (i == 0 or i == numControls - 1):
                jiggle = 0.0

            pm.addAttr(ctrl.control, longName='tangentLength', shortName='tanlen', minValue=0.0, defaultValue=1.0, keyable=True)
            pm.addAttr(ctrl.control, longName='jiggle', shortName='jig', defaultValue=jiggle, keyable=True)
            pm.addAttr(ctrl.control, longName='jiggleX', shortName='jigX', defaultValue=jiggle, keyable=True)
            pm.addAttr(ctrl.control, longName='jiggleY', shortName='jigY', defaultValue=jiggle, keyable=True)
            pm.addAttr(ctrl.control, longName='jiggleZ', shortName='jigZ', defaultValue=jiggle, keyable=True)
            pm.addAttr(ctrl.control, longName='jiggleImpact', shortName='jigimp', defaultValue=(0.5 * jiggle), keyable=True)
            pm.addAttr(ctrl.control, longName='jiggleImpactStart', shortName='jigimpst', defaultValue=1000, keyable=True)
            pm.addAttr(ctrl.control, longName='jiggleImpactStop', shortName='jigimpsp', defaultValue=0.001, keyable=True)
            pm.addAttr(ctrl.control, longName='cycle', shortName='cyc', minValue=1.0, defaultValue=12.0, keyable=True)
            pm.addAttr(ctrl.control, longName='rest', shortName='rst', minValue=1.0, defaultValue=24.0, keyable=True)
            for attr in ['tangentLength', 'jiggle', 'jiggleX', 'jiggleX', 'jiggleY', 'jiggleZ', 'jiggleImpact', 'jiggleImpactStart', 'jiggleImpactStop', 'cycle', 'rest']:
                pm.setAttr(ctrl.control +'.'+attr, lock=lockJiggleAttributes)

            if lockScale:
                # Unlock controls scale
                for xform in ['s']:
                    for axis in ['x', 'y', 'z']:
                        pm.setAttr(ctrl.control + '.' + xform + axis, lock=True, keyable=False)
            pm.setAttr(ctrl.control + '.visibility', lock=True, keyable=False)

            # Connect the attributes
            pm.connectAttr(ctrl.control + '.worldMatrix', self.splineNode + '.controlData[' + str(i) + '].insertMatrix')
            pm.connectAttr(ctrl.control + '.tangentLength', self.splineNode + '.controlData[' + str(i) + '].tangentLength')
            pm.connectAttr(ctrl.control + '.jiggle', self.splineNode + '.controlData[' + str(i) + '].jiggle')
            pm.connectAttr(ctrl.control + '.jiggleX', self.splineNode + '.controlData[' + str(i) + '].jiggleX')
            pm.connectAttr(ctrl.control + '.jiggleY', self.splineNode + '.controlData[' + str(i) + '].jiggleY')
            pm.connectAttr(ctrl.control + '.jiggleZ', self.splineNode + '.controlData[' + str(i) + '].jiggleZ')
            pm.connectAttr(ctrl.control + '.jiggleImpact', self.splineNode + '.controlData[' + str(i) + '].jiggleImpact')
            pm.connectAttr(ctrl.control + '.jiggleImpactStart', self.splineNode + '.controlData[' + str(i) + '].jiggleImpactStart')
            pm.connectAttr(ctrl.control + '.jiggleImpactStop', self.splineNode + '.controlData[' + str(i) + '].jiggleImpactStop')
            pm.connectAttr(ctrl.control + '.cycle', self.splineNode + '.controlData[' + str(i) + '].cycle')
            pm.connectAttr(ctrl.control + '.rest', self.splineNode + '.controlData[' + str(i) + '].rest')

        # # For each in-between control (not in the start and end control) we will use the constraint group above it and constraint it to the top and bottom
        # # groups. Doing this, mid controls will follow top and end controls. Also, we will aim constraints so in-between controls always aim starta and end
        # # controls

        blend = ""

        if constrainMid:
            for i in range(1, numControls - 1):

                # Get point constraint weight and create point constraint for intermediate controls
                pct = 1.0 * i / (numControls - 1.0)
                pm.pointConstraint(self.controls[0].control, self.consGrps[i], weight=(1.0 - pct))
                pm.pointConstraint(self.controls[numControls - 1].control, self.consGrps[i], weight=pct)

                # Create aim groups
                # We create one for the forward aim and another one for the back aim, then we have to
                # orient between both at the right amount
                grpAimFwd = pm.group(name=baseName + '_aimFwd_' + str(i) + '_' + suffixGrp, empty=True, world=True)
                grpAimBck = pm.group(name=baseName + '_aimBack_' + str(i) + '_' + suffixGrp, empty=True, world=True)
                for grp in [grpAimFwd, grpAimBck]:
                    snap(grp, self.controls[i].control)
                pm.sets(setRig, include=[self.rootGrps[i], grpAimFwd, grpAimBck])

                # Aim Forward group will aim the last control and Aim Back group will aim to the first control
                # This will give a twist behaviour on the aim groups
                aCons = pm.aimConstraint(self.controls[numControls - 1].control, grpAimFwd, weight=1, aimVector=(0, 1, 0),
                                         upVector=(1, 0, 0), worldUpVector=(1, 0, 0), worldUpType="objectrotation",
                                         worldUpObject=self.controls[numControls - 1].control)
                bCons = pm.aimConstraint(self.controls[0].control, grpAimBck, weight=1, aimVector=(0, -1, 0), upVector=(1, 0, 0),
                                         worldUpVector=(1, 0, 0), worldUpType="objectrotation",
                                         worldUpObject=self.controls[0].control)
                pm.sets(setRig, include=[aCons, bCons])

                # Now we drive the aims with the up info (we do this, only once) ...
                if i == 1:
                    # We make sure that the up axis attribute exists on  the cMuscleNode ...
                    if pm.objExists(self.splineNode + '.upAxis') != True:
                        pm.addAttr(self.splineNode, at="enum", longName="upAxis", enumName="X-Axis=0:Z-Axis=1", keyable=True)

                    # We use this blend to select the return the Z axis (vector 0,0,1) or X axis (vector 1,0,0)
                    blend = pm.createNode('blendColors', name=baseName + '_' + muscleSplineName + '_Aim_blend')
                    self.splineNode.upAxis.connect(blend.blender)
                    blend.color1.set(0, 0, 1)
                    blend.color2.set(1, 0, 0)
                    pm.sets(setRig, include=blend)

                # Each aim constraint up vector will follow the up axis attribute of the cMuscleSpineNode
                # We can switch between Z or X up axis if you get flipping when rotatig controls
                for cons in [aCons, bCons]:
                    blend.output.connect(cons.upVector)
                    blend.output.connect(cons.worldUpVector)

                # Aim groups also will follow start and end controls (so it will be positioned at the same position of its respective control)
                pConsFwd = pm.pointConstraint(self.controls[0].control, grpAimFwd, weight=(1.0 - pct))
                pConsFwd = pm.pointConstraint(self.controls[numControls - 1].control, grpAimFwd, weight=pct)
                pConsBack = pm.pointConstraint(self.controls[0].control, grpAimBck, weight=(1.0 - pct))
                pConsBack = pm.pointConstraint(self.controls[numControls - 1].control, grpAimBck, weight=pct)
                pm.sets(setRig, include=[pConsFwd, pConsBack])

                # The auto groups will follow the orientation of the aim groups
                # So, the controls (wihch are child of the auto groups) will follow the aim orientaiton
                oCons = pm.orientConstraint(grpAimBck, self.consGrps[i], weight=(1.0 - pct))
                oCons.interpType.set(2)
                oCons = pm.orientConstraint(grpAimFwd, self.consGrps[i], weight=pct)
                oCons.interpType.set(2)
                pm.sets(setRig, include=oCons)

                # At the end, we create root grops for each one of the aim groups (so its xfrorms are zeroed out)
                grpAimFwdRoot = pm.group(name=baseName + '_' + muscleSplineName + '_grpAimFwd_' + rootSuffix,
                                         empty=True, world=True)
                grpAimBckRoot = pm.group(name=baseName + '_' + muscleSplineName + '_grpAimBck_' + rootSuffix,
                                         empty=True, world=True)
                snap(grpAimFwdRoot, grpAimFwd)
                snap(grpAimBckRoot, grpAimBck)
                # snap(grpAimFwd, grpAimFwdRoot)
                # snap(grpAimBck, grpAimBckRoot)
                pm.sets(setRig, include=[grpAimFwdRoot, grpAimBckRoot])

                pm.parent(grpAimFwdRoot, self.rootGrps[i])
                pm.parent(grpAimFwd, grpAimFwdRoot)
                pm.parent(grpAimBckRoot, self.rootGrps[i])
                pm.parent(grpAimBck, grpAimFwdRoot)

        self.drivens = []

        for i in range(numDrivens):
            # Get normalized values between 0 and 1 and the correct name
            u = i / (numDrivens - 1.0)
            name = baseName + '_' + muscleSplineName + '_' + str(i) + '_' + suffixDrv

            if drivenType == "joint":
                self.drivens.append(pm.joint(name=name))
            elif drivenType == "circleY":
                ctrl = pm.circle(name=name, degree=3, center=[0, 0, 0], normal=[0, 1, 0], sweep=360, radius=1.0 * charSize,
                          useTolerance=False, sections=8, constructionHistory=False)[0]
                self.drivens.append(ctrl)
            else:
                self.drivens.append(pm.group(name=name, empty=True, world=True))

            pm.select(clear=True)

            pm.addAttr(self.drivens[i], longName="uValue", minValue=0.0, maxValue=1.0, defaultValue=u, keyable=True)
            pm.parent(self.drivens[i], self.drivensGrp)

            pm.sets(setRig, include=self.drivens[i])

            pm.connectAttr(self.drivens[i] + '.uValue', self.splineNode + '.readData[' + str(i) + '].readU', force=True)
            pm.connectAttr(self.drivens[i] + '.rotateOrder', self.splineNode + '.readData[' + str(i) + '].readRotOrder',
                           force=True)
            pm.connectAttr(self.splineNode + '.outputData[' + str(i) + '].outTranslate', self.drivens[i] + '.translate',
                           force=True)
            pm.connectAttr(self.splineNode + '.outputData[' + str(i) + '].outRotate', self.drivens[i] + '.rotate', force=True)

        len = self.splineNode.outLen.get()
        self.splineNode.lenDefault.set(len)
        self.splineNode.lenSquash.set(len * 0.5)
        self.splineNode.lenStretch.set(len * 2.0)

        pm.select(self.mainGrp)

        return self.splineNode

def initUI():
    tpMuscleSplineRigWin().show()
