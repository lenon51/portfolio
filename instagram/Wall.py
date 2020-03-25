from datetime import date
from datetime import datetime
import random
from ImageDetect import ImageDetect
from Instagram import Instagram 
from DataBase import DataBase
from Untappd import Untappd
from TypeSource import TypeSource
import pandas as pd
import re
import numpy as np
import os
import pickle
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
import nltk
from stop_words import  get_stop_words
from nltk.stem import WordNetLemmatizer
class Wall:
    def __init__(self, mobile=False):
        self.user = ''
        self.insta = Instagram(self.user,'',user_agent_mobile=mobile)
        self.unta = Untappd('3BA9000EAF1D1AFA9A5F243A6075061EE032EB0D','57B991CB52528E6F4116570B97AA00B3AA04430A')	
        self.data = DataBase()
        self.insta.signIn()
        
    def __del__(self):
        self.insta.closeBrowser()
        
    def saveSource(self, source, type_source, withHistory = True, source_hierarchy=None):
        '''Salvar uma conta ou hashtag'''
    
        lst_source = self.data.searchSource(source, type_source)
        if  len(lst_source) == 0:
            self.data.saveSource(source, type_source, date.today(), source_hierarchy)
            lst_source = self.data.searchSource(source, type_source) 
        
        if type_source != TypeSource.Hashtag and withHistory:            
            lst = self.insta.getAccount(source)
            if len(lst) > 0:
                self.data.saveSourceHistory(lst['post'], 
                                            lst['follower'], 
                                            lst['follow'], 
                                            lst_source[0]['id_origem'], 
                                            datetime.now())    
    def saveFollower(self, source):
        '''Salvar seguidores de uma conta'''
        lst_source = self.data.searchSource(source, TypeSource.Account)
        if len(lst_source) == 0:
            self.saveSource(source, TypeSource.Account)
            lst_source = self.data.searchSource(source, TypeSource.Account)

        lst_insta = self.insta.getFollower(source)   
        lst_db = self.data.searchSourceHierarchy(lst_source[0]['id_origem'])
        lst_follower = []        
        for item in lst_insta:
            if len(list(filter(lambda x: x['nm_origem'] == item, lst_db))) == 0:
                lst_follower.append((item, 
                                     date.today(), 
                                     TypeSource.Follower.value, 
                                     lst_source[0]['id_origem']))
        
        if len(lst_follower) > 0:
            self.data.saveSourceList(lst_follower)
            
    def saveFollowerHistoric(self, source=None):
        '''Salvar histórico dos seguidores de uma conta'''

        i = 0
        id_source = 0
        if source != None:
            lst_source = self.data.searchSource(source, TypeSource.Account)
            if len(lst_source) == 0:
                return
            id_source = lst_source[0]['id_origem']
            
        lst_db = self.data.searchSourceHierarchy(id_source, False)
        for item in lst_db:
            if i >= 50:
                return
            
            lst = self.insta.getAccount(item['nm_origem'])
            genre = self.saveFollowGenre(item['nm_origem'])
            
            if len(lst) > 0 and int(lst['follower']) > 0:
                self.data.saveSourceHistory(lst['post'], 
                                            lst['follower'], 
                                            lst['follow'], 
                                            item['id_origem'],
                                            lst['private'],
                                            datetime.now(),
                                            genre,
                                            lst['bio'])
            else:
                self.data.saveSourceHistory(0, 
                                            0, 
                                            0, 
                                            item['id_origem'], 
                                            False,
                                            datetime.now(),
                                            genre,
                                            '')
            i +=1        
    
    def savePictures(self, type_source, source=None):
        '''Salvar uma lista de imagem de uma conta'''
        
        if source == None:
            lst_source = self.data.searchSourceByType(type_source)
        else:
            lst_source = self.data.searchSource(source, type_source)
            if len(lst_source) == 0:
                return

        lst_picture = []
        for item_source in lst_source:
            lst_tag = self.insta.searchPicture(item_source['nm_origem'], type_source)
            for item in lst_tag:
                if len(self.data.searchPicture(item)) == 0:
                    lst_picture.append((item_source['id_origem'], 
                                        item,
                                        date.today()))              
        
        if len(lst_picture) > 0:
            self.data.savePicture(lst_picture)
    
    def savePictureHistoric(self):
        '''Salvar dados da foto'''
        lst_pic = self.data.searchPicture()

        lst_historic = []
        i = 0
        for item in lst_pic:
            if i > 100:
                break
            
            pic_historic = self.insta.getPictureHistoric(item['nm_url_foto'])
            if pic_historic['like'] > 0:
                lst_historic.append((pic_historic['user'],
                                     pic_historic['like'],
                                     pic_historic['date'],
                                     pic_historic['description'],
                                     pic_historic['tag'],
                                     item['nm_url_foto']))
            else:
                self.data.updatePictureValid(item['nm_url_foto'], False)
            i += 1

        self.data.updatePictureHistoric(lst_historic)
                    
        #salvar hashtags
        lst_hashtag = self.searchHashTag()
        f = open("hashtag.txt", "w")
        f.write(lst_hashtag)
        f.close()
            
    def saveComment(self):
        '''Salvar comentários e curtidas em fotos'''
        lst_picture = self.data.searchPictureComment()
        qty_picture = 0
        lst_phrase = self.data.searchPhrase(TypeSource.Comment)
        emoji = '\U0001F37B\U0001F37A'
        for item in lst_picture:
            if qty_picture >=2:
                break
                
            phrase = lst_phrase[random.randint(0,len(lst_phrase)-1)]            
            self.insta.saveLike(item['nm_url_foto'])
            self.insta.saveComment(item['nm_url_foto'], 
                                   phrase['ds_frase'] + emoji)
            self.data.updatePictureComment(item['nm_url_foto'], 
                                           date.today(), 
                                           phrase['ds_frase'], 
                                           date.today(),
                                           True,
                                           True)
            qty_picture += 1
    
    def savePictureRepost(self):
        '''Repostar foto'''
        #lst_picture = self.data.searchPicture(to_post=True)
        lst_picture = self.searchImageML()
        if len(lst_picture) == 0:
            return
        
        picture = lst_picture[0]        
        lst_phrase = self.data.searchPhrase(TypeSource.Post)
        phrase = lst_phrase[random.randint(0,len(lst_phrase)-1)]
        
        filename = self.insta.getPost(picture['nm_url_foto'])
        print(filename)
        if filename == None or not self.IsValidImage(filename):
            print('Buscando outra imagem...')
            if filename != None and os.path.exists(filename):
                os.remove(filename)
            self.data.updatePictureValid(picture['nm_url_foto'], False)
            self.savePictureRepost()
        else:
            emoji = '\U0001F37B\U0001F37A'
            #ler hashtags
            f = open("hashtag.txt", "r")
            lst_hashtag = f.read()
            comment = '{}{} ⠀⠀⠀⠀⠀⠀⠀⠀⠀ . ⠀⠀⠀⠀⠀⠀⠀⠀⠀ by @{} / {} ⠀⠀⠀⠀⠀⠀⠀⠀⠀ . ⠀⠀⠀⠀⠀⠀⠀⠀⠀ {}'.format(phrase['ds_frase'],
                                                                                               emoji,
                                                                                       picture['nm_usuario_foto'],
                                                                                 ' / '.join(set(re.findall('@[a-zA-Z_]+',str(picture['ds_foto']).lower()))),
                                                                                 lst_hashtag)
            self.insta.postPicture(filename, comment)
            self.data.updatePictureRepost(picture['nm_url_foto'], 
                                          date.today(), 
                                          comment, 
                                          repost=True)
            
            for item in lst_hashtag:
                if len(item) > 3:
                    self.saveSource(item.replace('#',''), TypeSource.Hashtag)
        
            if os.path.exists(filename):
                os.remove(filename)            

    def saveFollow(self):
        '''Seguir e salvar'''
        lst_source = self.data.searchFollower()
        #lst_source = self.searchFollowTop()
        print(lst_source)
        for item in lst_source:
            exists = self.insta.followUser(item['nm_origem'])
            print(exists)
            if exists:
                self.data.saveFollow(item['id_origem'], date.today())
    
    
    def searchFollowTop(self):
        '''Consultar e predizer quais melhores usuário para seguir'''
        data_ml = pd.DataFrame(self.data.searchFollow(False))
        data_ml.sg_sexo = data_ml.sg_sexo.apply(lambda x: 'I' if (x == '') else x)
        data_ml.sg_sexo.fillna(value='I', inplace=True)
        data_ml = data_ml.join(pd.get_dummies(data_ml.sg_sexo.apply(pd.Series).stack()).sum(level=0))
        data_ml = data_ml.join(pd.get_dummies(data_ml.nm_pai.apply(pd.Series).stack()).sum(level=0))
        loaded_model = pickle.load(open('model.sav', 'rb'))
        result = loaded_model.predict(data_ml[['qt_publicacao',
                                               'qt_seguidor',
                                               'qt_seguindo',
                                               'ic_privado',
                                               'F','M','I',
                                               'bicudobrewing',
                                               'caiscervejaartesanal',
                                               'cervejademonho',
                                               'infectedbrewingco']])
        data_ml['ic_retorno'] = result
        data_ml = data_ml[data_ml.ic_retorno == 1].head(30)[['id_origem','nm_origem']]
        return data_ml.T.to_dict().values()

    def saveFollowML(self):
        data_ml = pd.DataFrame(self.data.searchFollow())
        data_ml.sg_sexo = data_ml.sg_sexo.apply(lambda x: 'I' if (x == '') else x)
        data_ml.sg_sexo.fillna(value='I', inplace=True)
        data_ml.ic_retorno.fillna(value=0, inplace=True)
        data_ml = data_ml.join(pd.get_dummies(data_ml.sg_sexo.apply(pd.Series).stack()).sum(level=0))
        data_ml = data_ml.join(pd.get_dummies(data_ml.nm_pai.apply(pd.Series).stack()).sum(level=0))
        data_ml = data_ml[['qt_publicacao',
                           'qt_seguidor',
                           'qt_seguindo',
                           'ic_privado',
                           'ic_retorno',
                           'F','M','I',
                           'bicudobrewing',
                           'caiscervejaartesanal',
                           'cervejademonho',
                           'infectedbrewingco']]
        data_ml.drop(data_ml[data_ml.ic_privado.isnull()].index, inplace=True)
        data_ml.ic_retorno = data_ml.ic_retorno.astype(int)
        x_train, x_test, y_train, y_test = train_test_split(data_ml[[item for item in data_ml.columns if item not in ['ic_retorno']]],
                                                            data_ml.ic_retorno,
                                                            test_size=0.2,
                                                            random_state=42)
        clf = RandomForestClassifier(max_depth=5, random_state=42, n_estimators=100, class_weight="balanced")
        clf.fit(x_train, y_train)
        pickle.dump(clf, open('model.sav', 'wb'))
    
    def saveUnfollow(self):
        '''Desseguir e salvar'''
        lst_source = self.data.searchUnfollower()
        for item in lst_source:
            exists = self.insta.unfollowUser(item['nm_origem'])
            if exists:
                self.data.saveUnfollow(item['id_origem'],date.today())

    def saveBrewery(self):
        '''Salvar cervejarias e suas cervejas'''
        lst_brewery = [278580, 354747, 362211, 383207, 226157] #Cervejarias santistas
        df = pd.DataFrame()
        for i in lst_brewery:
            df = df.append(self.unta.searchBrewery(i))
        df.nota = df.id.apply(lambda x: self.unta.searchBeerRating(x))
        
        self.data.saveBrewery(df[['cervejaria_id', 
                                    'cervejaria',
                                    'facebook',
                                    'instagram',
                                    'cidade',
                                    'uf',
                                    'latitude',
                                    'longitude',
                                    'url']].drop_duplicates().fillna('').values.tolist())
        
        self.data.saveBeer(df[['id',
                                'cervejaria_id',
                                'cerveja',
                                'estilo',
                                'abv',
                                'ibu',
                                'total_checkin',
                                'logo',
                                'nota']].fillna('').values.tolist())
        
    def searchCheckIn(self):
        lst_beer = self.data.searchBeer()
        
        for item in lst_beer:
            page = None
            if item['nr_ultima_pagina'] == 0:
                #chegou na última página
                continue                        
            elif item['nr_ultima_pagina'] != '':
                page = item['nr_ultima_pagina']
            
            df_check = self.unta.searchBeerCheckIn(item['id_cerveja'], page)

            if df_check is not None and len(df_check) > 0:
                df_check['id_cerveja'] = item['id_cerveja']
                df_check.data = df_check.data.apply(lambda x: str(datetime.strptime(x, '%a, %d %b %Y %H:%M:%S %z').replace(tzinfo=None)))

                self.data.saveUser(df_check[['id_usuario',
                                             'usuario',
                                             'nome',
                                             'sobrenome',
                                             'biografia',
                                             'url_usuario']].drop_duplicates().fillna('').values.tolist())

                self.data.saveCheckIn(df_check[['id_usuario',
                                                'id_cerveja', 
                                                'data',
                                                'nota',
                                                'comentario',
                                                'localizacao',
                                                'local_id',
                                                'local_nome',
                                                'plataforma',
                                                'local_cidade',
                                                'local_uf',
                                                'local_lat',
                                                'local_lng']].fillna('').values.tolist())
            
                self.data.saveCheckInPage(str(df_check['proxima_pagina'].loc[0]), item['id_cerveja'])
            else:
                self.data.saveCheckInPage('0', item['id_cerveja'])
                
    def saveCheckUser(self):
        lst_user = self.data.searchUser()
        for item in lst_user:
            
            page = None
            if item['nr_ultima_pagina'] == 0:
                #chegou na última página
                continue                        
            elif item['nr_ultima_pagina'] != '':
                page = item['nr_ultima_pagina']
            
            df_user = self.unta.searchUser(item['nm_login'], page)
            if df_user is not None and len(df_user) > 0:
                print(item['nm_login'])
                self.data.saveInfoUser(df_user[['total_checkin',
                                                'total_amigo',
                                                'total_cerveja',
                                                'total_seguidores',
                                                'total_foto',
                                                'foto_capa',
                                                'proxima_pagina',
                                                'id_usuario']].fillna('').values.tolist())

                df_checkin = json_normalize(df_user.loc[0].checkin_outro)                 
                if len(df_checkin) > 1:
                    df_checkin['id_usuario'] = item['id_usuario']
                    df_checkin.created_at = df_checkin.created_at.apply(lambda x: str(datetime.strptime(x, '%a, %d %b %Y %H:%M:%S %z').replace(tzinfo=None)))

                    if 'venue.venue_id' not in df_checkin.columns:
                        df_checkin['venue.venue_id'] = 0
                        
                    self.data.saveCheckInUser(df_checkin[['checkin_id',
                                                           'beer.bid',
                                                           'id_usuario',
                                                           'beer.beer_style',                                                   
                                                           'beer.beer_name',
                                                           'brewery.brewery_name',
                                                           'venue.venue_id',
                                                           'created_at']].fillna('').values.tolist())
            else:
                self.data.saveCheckInUserPage('0', item['id_usuario'])

    def searchHashTag(self):
        data = pd.DataFrame(self.data.searchPicture(all=True))
        #retira as hashtags da descrição da foto e soma a quantidade de contas marcadas na foto
        data['nm_hashtag'] = data.ds_foto.apply(lambda x: re.findall('#[a-zA-Z]+',str(x).lower()))
        data['qt_marcado'] = data.nm_tag.apply(lambda x: len(str(x).split(',')) if str(x) != 'nan' else 0)
        #transforma a lista de hashtags em colunas, somando o total de hashtags por foto
        data = data.join(pd.get_dummies(data[data.qt_curtida_foto > 10].nm_hashtag.apply(pd.Series).stack()).sum(level=0))
        #criação do dataframe para a tentativa de prever as curtidas através das hashtags e quantidade de pessoas marcadas
        # retiro as fotos que não tem curtidas
        data_ml = data[[col for col in data.columns if '#' in col]]
        data_ml = data[['qt_marcado','qt_curtida_foto']].join(data_ml)
        data_ml.fillna(0, inplace=True)
        data_ml = data_ml[data_ml.qt_curtida_foto > 10]
        #treinando e separando os dados
        x_train, x_test, y_train, y_test = train_test_split(data_ml[[item for item in data_ml.columns if item not in ['qt_curtida_foto','qt_marcado']]],
                                                            data_ml.qt_curtida_foto,
                                                            test_size=0.2,
                                                            random_state=42)
        tree = DecisionTreeClassifier(min_samples_leaf=5)
        tree.fit(x_train, y_train)
        y_pred = tree.predict(x_test)
        lst_hashtag = sorted(list(zip(x_train.columns, tree.feature_importances_)), key=lambda x : x[1], reverse=True)
        return ' '.join([item[0] for item in lst_hashtag][:5])

    def IsValidImage(self, image):
        img = ImageDetect()
        valid = img.read_image(image)
        del img
        return valid
    
    def saveFollowBack(self):
        lst_insta = self.insta.getFollower(self.user)
        self.data.saveFollowBack(lst_insta)
        
    def saveFollowGenre(self, user):
        name = ''
        lst_name = []
        for word in list(''.join(re.findall('[^\W _\d]',user))):
            if len(name) >= 3:
                lst_name.append(name.upper())
            name += word

        df_genere = pd.read_csv('genero-nomes.csv')
        df = df_genere[df_genere.first_name.isin(lst_name)]
        val = df[df.ratio == df.ratio.max()].classification
        if len(val) > 0:
            return val.values[0]
        return ''       
        
    def saveImageML(self):
        '''Salvar modelo preditivo para as imagens'''

        data_ml = self.searchImageMLDataFrame()
        data_val = pd.read_csv('insta_picture_url.csv',sep=';')
        data_img = pd.merge(data_ml, data_val, left_on=['nm_url_foto'],right_on=['url'])
        data_img = data_img[['qt_curtida_foto',
                             'qt_hashtag',
                             'qt_dia_post',
                             'qt_media_curtida',
                             'qt_palavra',
                             'boa',
                             'nm_url_foto']]
        x_train, x_test, y_train, y_test = train_test_split(data_img[[item for item in data_img.columns if item not in ['boa','nm_url_foto']]],
                                                            data_img.boa,
                                                            test_size=0.2,
                                                            random_state=42)
        logres_img = LogisticRegression(solver='lbfgs',multi_class='auto')
        logres_img.fit(x_train, y_train)
        pickle.dump(logres_img, open('model_img.sav', 'wb'))
    
    def searchImageML(self):
        data_ml = self.searchImageMLDataFrame()
        loaded_model = pickle.load(open('model_img.sav', 'rb'))
        data_ml = data_ml[data_ml.ic_repostado == 0]
        df_predict = loaded_model.predict(data_ml[['qt_curtida_foto',
                                                   'qt_hashtag',
                                                   'qt_dia_post',
                                                   'qt_media_curtida',
                                                   'qt_palavra']])
        data_ml['boa'] = df_predict
        data_ml = data_ml[data_ml.boa == 1]
        return list(data_ml.head(2).T.to_dict().values())
    
    def searchImageMLDataFrame(self):
        def limpar_texto(s):
            '''Limpar texto'''

            if s == None:
                return ''

            s = str(s)
            #retiro as hashtags
            s = ' '.join(set(re.findall('[#a-zA-Z_]+', s.lower())) - 
                         set(re.findall('#[a-zA-Z_0-9]+', s.lower()))).replace('#','')
            #print(s)
            lst_word = []
            lemmatizer = WordNetLemmatizer()
            for item in s.split(' '):
                word = lemmatizer.lemmatize(item)
                if word == item:
                    word = lemmatizer.lemmatize(item, pos='v')
                lst_word.append(item)   

            lst_word = set(lst_word) - set(get_stop_words('pt'))
            lst_word = set(lst_word) - set(get_stop_words('en'))

            return ' '.join(lst_word)
        nltk.download('wordnet')
        
        data_ml = pd.DataFrame(self.data.searchPicture(to_model=True))
        data_ml['nm_hashtag'] = data_ml.ds_foto.apply(lambda x: re.findall('#[a-zA-Z_0-9]+',str(x).lower()))
        data_ml['qt_marcado'] = data_ml.nm_tag.apply(lambda x: len(str(x).split(',')) if str(x) != 'nan' else 0)
        data_ml['qt_hashtag'] = data_ml.nm_hashtag.apply(lambda x: len(list(x)) if str(x) != 'nan' else 0)
        data_ml.dt_foto = pd.to_datetime(data_ml['dt_foto'])
        data_ml.dt_leitura = pd.to_datetime(data_ml['dt_leitura'])
        data_ml['qt_dia_post'] = data_ml.dt_leitura - data_ml.dt_foto
        data_ml.qt_dia_post = data_ml.qt_dia_post.apply(lambda x: round(x.total_seconds() / 3600 / 24) if round(x.total_seconds() / 3600 / 24) > 0 else 0)
        data_ml['qt_media_curtida'] = data_ml[['qt_curtida_foto',
                                               'qt_dia_post']].apply(lambda x: x['qt_curtida_foto'] / x['qt_dia_post'] if x['qt_dia_post'] > 0 else x['qt_curtida_foto'] , axis=1)
        data_ml['ds_texto_limpo'] = data_ml.ds_foto.apply(lambda x: limpar_texto(x))
        data_ml['qt_palavra'] = data_ml.ds_texto_limpo.apply(lambda x: len(x.split(' ')))
        
        return data_ml[data_ml.qt_curtida_foto > 10]
    
    def getStories(self):
        self.insta.getStories()