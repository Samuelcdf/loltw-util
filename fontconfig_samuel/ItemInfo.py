#coding: utf8
'''
Created on Mar 14, 2012

@author: samuel.lee
'''

import PackageConfig;

import re;
import codecs;


def get_rune_total_desc(RuneMap):
    ReturnEffectDescriptionList = [];
    
    EffectMap = {};
    for (RuneID, Quantity) in RuneMap.iteritems():
        for MatchObject in InfoMap["Item"][unicode(RuneID)]["__MatchObjectList"]:
            if(RuneID == 0):
                pass;
            elif(MatchObject.re == ParserMap["Rune_Unique"]):
                EffectMap[MatchObject.string] = MatchObject.string;
            else:
                Flag = "F";
                if(MatchObject.re == ParserMap["Rune_Grow"]):
                    Flag = "G";
                Data = MatchObject.group(1);
                if(Data.endswith("%") == True):
                    Flag += "P";
                    Data = Data[:-1];
                    
                EffectName = "%s_%s" % (Flag, MatchObject.group(3));
                if(EffectName not in EffectMap):
                    EffectMap[EffectName] = 0;
                EffectMap[EffectName] += float(Data) * Quantity;
            
    for (Name, Value) in EffectMap.iteritems():
        if(Name.startswith("G_") == True):
            Value = u"%+.2f %s 每級 (%+.2f 18級)" % (Value, Name[2:], Value*18);
        elif(Name.startswith("GP_") == True):
            Value = u"%+.2f%% %s 每級 (%+.2f%% 18級)" % (Value, Name[3:], Value*18);
        elif(Name.startswith("F_") == True):
            Value = u"%+.2f %s" % (Value, Name[2:]);
        elif(Name.startswith("FP_") == True):
            Value = u"%+.2f%% %s" % (Value, Name[3:]);

        ReturnEffectDescriptionList.append(Value);
    
    return ReturnEffectDescriptionList;

def get_talent_desc(MasteryID, Rank):
    ReturnString = "";
    
    MasteryID = unicode(MasteryID);
    if(MasteryID in InfoMap["Mastery"]):
        ReturnString = InfoMap["Mastery"][MasteryID]["level%ddesc" % int(Rank)];
    else:
        raise Exception("Given MasteryID Doesn't Exist");
    
    return ReturnString;

def __InitializeParserMap():
    ReturnMap = {};

    ReturnMap["Global"] = re.compile(u"tr \"(\w+)_(\d+)\" = \"(.*?)\"", re.IGNORECASE | re.UNICODE);

    #1 6 183 246
    ReturnMap["Rune_5367"] = re.compile(u"唯一.+", re.IGNORECASE | re.UNICODE);
    ReturnMap["Rune_Unique"] = re.compile(u"唯一.+", re.IGNORECASE | re.UNICODE);    
    ReturnMap["Rune_Grow"] = re.compile(u".*?([+-]?\d+(\.\d+)?%?)\s*(.+?)\s*每級\s*.+?([+-]?\d+(\.\d+)?)%?\s*18級.+?", re.IGNORECASE | re.UNICODE);
    ReturnMap["Rune_Fix"] = re.compile(u".*?([+-]?\d+(\.\d+)?%?)\s*(.+)", re.IGNORECASE | re.UNICODE);
    
    return ReturnMap;

def __Initialize():
    ReturnMap = {"Item": {}, "Mastery": {}};
    
    InputFile = codecs.open(PackageConfig.AbsolutePath_FontConfig, "rb", "utf8");
    for Line in InputFile:
        MatchObject = ParserMap["Global"].match(Line.strip());
        if(MatchObject != None):
            InfoTuple = MatchObject.groups();
            
            if(InfoTuple[0].find("game_item") != -1):
                KeyName = InfoTuple[0][len("game_item")+1:];
                ItemInfoMap = ReturnMap["Item"].setdefault(InfoTuple[1], {});
                ItemInfoMap[KeyName] = InfoTuple[2];
            elif(InfoTuple[0].find("game_mastery") != -1):
                KeyName = InfoTuple[0][len("game_mastery")+1:];
                ItemInfoMap = ReturnMap["Mastery"].setdefault(InfoTuple[1], {});
                ItemInfoMap[KeyName] = InfoTuple[2];
    InputFile.close();
    
    return ReturnMap;

def __ProcessRuneInfo():
    ParserRuleNameList = ["Rune_Unique", "Rune_Grow", "Rune_Fix"];
    
#    RuneNameList = [u"印記", u"雕文", u"紋章", u"精髓", u"Mark", u"Glyph", u"Seal", u"Quintessence"];
    RuneNameList = [u"印記", u"文", u"紋章", u"精髓", u"Mark", u"Glyph", u"Seal", u"Quintessence"];
    
    for ItemInfoMap in InfoMap["Item"].itervalues():
        try:
            bIsRune = False;
            for RuneName in RuneNameList:
                if(RuneName in ItemInfoMap["displayname"]):
                    bIsRune = True;
                    break;
            if(bIsRune == False):
                continue;

            DescriptionGenerator = (Description.strip() for Description in ItemInfoMap["description"].split("/"));
            for Description in DescriptionGenerator:
                MatchObject = None;
                for RuleName in ParserRuleNameList:
                    if(MatchObject != None):
                        break;
                    MatchObject = ParserMap[RuleName].match(Description);
                    
                if(MatchObject != None):
                    if("__MatchObjectList" not in ItemInfoMap):
                        ItemInfoMap["__MatchObjectList"] = [];
                    ItemInfoMap["__MatchObjectList"].append(MatchObject);
                else:
                    break;
        except:
            pass;
        

ParserMap = __InitializeParserMap();
InfoMap = __Initialize();
__ProcessRuneInfo();
