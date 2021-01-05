import os,argparse,logging,xlsxwriter,twint,json

#KEY WORK ASSGIN PART
ID = "id"
HASH = "#"
TWEETS = "tweets"
LINK = "link"
SHEET1 = "Tweets in HashTag"
SHEET2 = "Report in HashTag"
USER_ID = "user_id"
REPLIES = "replies_count"
RETWEET =  "retweets_count"
LIKE = "likes_count"
CREATED_AT = "created_at"
SCREEN_NAME = "name"
USER_NAME = "username"
LIBPATH = os.path.join(os.getcwd(),"lib")
TMPPATH = os.path.join(LIBPATH,"tmp.txt")


class AssginTweetData():
    def __init__(self,args):
        self.config = twint.Config()
        self.name_of_hashtag = args.hashtag
        self.config.Limit = 100000000000000000
        self.basic_setup_status = self.basicSetup()

    def manager(self):
        try:
            store_tmp_file = self.storeTmpFile()
            if store_tmp_file is True:
                composeJsonFile = self.composeJsonFileFun()
                if composeJsonFile is not None:
                    wrapFormat = self.buildJsonFormat(composeJsonFile)
                    if wrapFormat is not None:
                        writeXlsxSheet = self.writeXlsxSheetFun(wrapFormat)
                        if writeXlsxSheet is True:
                            logging.info("Finish")
                            if os.path.isfile(TMPPATH):
                                os.remove(TMPPATH)
                    else:
                        logging.error("not build json")
                else:
                    logging.error("not convert json file")
            else:
                logging.error("error to crawler")
        except Exception as e:
            logging.error(e)
            return False

    def writeXlsxSheetFun(self,Data):
        try:
            A = "A{0}"
            B = "B{0}"
            C = "C{0}"
            D = "D{0}"
            E = "E{0}"
            F = "F{0}"
            G = "G{0}"
            H = "H{0}"
            itemCounter = 2
            indexs1 = ["A","B","C","D","E","F","G","H"]
            titles1 = [ID,CREATED_AT,USER_ID,USER_NAME,LINK,REPLIES,RETWEET,LIKE]
            indexs2 = ["A","B","C"]
            titles2 = [USER_ID,USER_NAME,"Total_Tweet"]
            xlsxFileName = self.name_of_hashtag+".xlsx"
            if os.path.isfile(xlsxFileName):
                os.remove(xlsxFileName)
            workbook = xlsxwriter.Workbook(xlsxFileName)
            workbookSheet1 = workbook.add_worksheet(SHEET1)
            for index,title in zip(indexs1,titles1):
                workbookSheet1.write("{0}1".format(index),str(title))
            workbookSheet2 = workbook.add_worksheet(SHEET2)
            for index,title in zip(indexs2,titles2):
                workbookSheet2.write("{0}1".format(index),str(title))
            for items in Data:
                tmpUserName = Data[items][USER_NAME]
                for tweetItem in Data[items][TWEETS]:
                    tmpTweetId = tweetItem[ID]
                    tmpDate = tweetItem[CREATED_AT]
                    tmpLink = tweetItem[LINK]
                    tmpReplice = tweetItem[REPLIES]
                    tmpRetweet = tweetItem[RETWEET]
                    tmpLike = tweetItem[LIKE]
                    if tmpLike is None:
                        tmpLike = 0
                    workbookSheet1.write(A.format(itemCounter),str(tmpTweetId))
                    workbookSheet1.write(B.format(itemCounter),str(tmpDate))
                    workbookSheet1.write(C.format(itemCounter),str(items))
                    workbookSheet1.write(D.format(itemCounter),str(tmpUserName))
                    workbookSheet1.write(E.format(itemCounter),str(tmpLink))
                    workbookSheet1.write(F.format(itemCounter),str(tmpReplice))
                    workbookSheet1.write(G.format(itemCounter),str(tmpRetweet))
                    workbookSheet1.write(H.format(itemCounter),str(tmpLike))
                    itemCounter += 1
            itemCounter = 2
            for items in Data:
                tmpUserName = Data[items][USER_NAME]
                tweetCount = len(Data[items][TWEETS])
                workbookSheet2.write(A.format(itemCounter),str(items))
                workbookSheet2.write(B.format(itemCounter),str(tmpUserName))
                workbookSheet2.write(C.format(itemCounter),str(tweetCount))
                itemCounter += 1
            workbook.close()
            return True
        except Exception as e:
            logging.error(e)
            return None

    def buildJsonFormat(self,js):
        try:
            BUILD = dict()
            for item in js:
                USER_ID_STR = str(item[USER_ID])
                if USER_ID_STR in BUILD:
                    tweetDict = dict()
                    tweetDict[ID] = item[ID]
                    tweetDict[CREATED_AT] = item[CREATED_AT]
                    tweetDict[LINK] = item[LINK]
                    tweetDict[REPLIES] = item[REPLIES]
                    tweetDict[RETWEET] = item[RETWEET]
                    tweetDict[LIKE] = item[LIKE]
                    BUILD[USER_ID_STR][TWEETS].append(tweetDict)
                else:
                    BUILD[USER_ID_STR] = dict()
                    BUILD[USER_ID_STR][USER_NAME] = item[USER_NAME]
                    BUILD[USER_ID_STR][SCREEN_NAME] = item[SCREEN_NAME]
                    BUILD[USER_ID_STR][TWEETS] = list()
                    tweetDict = dict()
                    tweetDict[ID] = item[ID]
                    tweetDict[CREATED_AT] = item[CREATED_AT]
                    tweetDict[LINK] = item[LINK]
                    tweetDict[REPLIES] = item[REPLIES]
                    tweetDict[RETWEET] = item[RETWEET]
                    tweetDict[LIKE] = item[LIKE]
                    BUILD[USER_ID_STR][TWEETS].append(tweetDict)
            return BUILD
        except Exception as e:
            logging.error(e)
            return None

    def composeJsonFileFun(self):
        try:
            if os.path.isfile(TMPPATH):
                tmpList = list()
                with open(TMPPATH,"r+") as fs:
                    linesContent = fs.readlines()
                    for line in linesContent:
                        contentJson = json.loads(line)
                        tmpList.append(contentJson)
                fs.close()
                return tmpList
            return None
        except Exception as e:
            logging.error(e)
            return None

    def storeTmpFile(self):
        try:
            if os.path.isfile(TMPPATH):
                os.remove(TMPPATH)
            self.config.Search = HASH+str(self.name_of_hashtag)
            self.config.Store_json = True
            # self.config.Location=True
            # self.config.Limit = 10
            self.config.Output = TMPPATH
            twint.run.Search(self.config)
            return True
        except Exception as e:
            logging.error(e)
            return False

    def basicSetup(self):
        try:
            if not os.path.isdir(LIBPATH):
                os.makedirs(LIBPATH)
            return True
        except Exception as e:
            logging.info(e)
            return False


if __name__ == "__main__":
    logging.basicConfig(level="INFO")
    parser = argparse.ArgumentParser()
    parser.add_argument("-s","--hashtag",help="enter the hash tag",required=True)
    args = parser.parse_args()
    AssginTweetData(args).manager()