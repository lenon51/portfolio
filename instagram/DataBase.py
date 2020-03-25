import pymysql
import pymysql.cursors
class DataBase():
    def __init__(self):
        self.connection = None

    def open(self):
        self.connection = pymysql.connect(host='',
                                         user='',
                                         password='',
                                         db='',
                                         cursorclass=pymysql.cursors.DictCursor)        
        
    def saveSource(self, source, type_source, source_date, source_hierarchy=None):
        '''Salvar uma conta ou hashtag'''
        self.open()
        try:
            with self.connection.cursor() as cursor:
                sql = "insert into insta_origem (nm_origem, dt_leitura, id_tipo_origem, id_origem_pai) values (%s, %s, %s, %s)"
                cursor.execute(sql, (source, source_date, type_source.value, source_hierarchy))
                self.connection.commit()
        finally:
            self.connection.close()
    
    def saveSourceList(self, list_source):
        '''Salvar várias contas'''
        self.open()
        try:
            with self.connection.cursor() as cursor:
                sql = "insert ignore into insta_origem (nm_origem, dt_leitura, id_tipo_origem, id_origem_pai) values (%s, %s, %s, %s)"
                cursor.executemany(sql, list_source)
                self.connection.commit()
        finally:
            self.connection.close()
            
    def savePicture(self, lst_picture):
        '''Salvar fotos para postar, comentar ou curtir'''
           
        self.open()
        try:
            with self.connection.cursor() as cursor:               
                sql = 'insert ignore into insta_foto(id_origem, nm_url_foto, dt_leitura, qt_curtida_foto, ic_comentado, ic_curtido, ic_repostado, ic_imagem)'
                sql += 'values(%s, %s, %s, 0, 0, 0, 0, 1)'
                cursor.executemany(sql, lst_picture)
                self.connection.commit()
        finally:
            self.connection.close()
        
    def searchSource(self, source, type_source):
        '''Consultar a conta ou hashtag'''
        self.open()
        try:
            with self.connection.cursor() as cursor:
                sql = 'select id_origem, nm_origem from insta_origem where nm_origem = %s and id_tipo_origem = %s'
                cursor.execute(sql, (source, type_source.value))
                results = cursor.fetchall()             
        finally:
            self.connection.close()
        
        return results

    def searchSourceByType(self, type_source):
        '''Consultar a conta ou hashtag'''
        self.open()
        try:
            with self.connection.cursor() as cursor:
                sql = 'select id_origem, nm_origem from insta_origem where id_tipo_origem = %s'
                cursor.execute(sql, (type_source.value))
                results = cursor.fetchall()             
        finally:
            self.connection.close()
        
        return results
    
    def searchSourceHierarchy(self, source_hierarchy, withHistoric=True):
        '''Consultar origem por origem pai'''
        
        sql_exists = ''
        if not withHistoric:
            sql_exists = ' and not exists (select 1 from insta_origem_historico his where his.id_origem = ori.id_origem)'
            
        if source_hierarchy == 0:
            sql = 'select ori.id_origem, ori.nm_origem from insta_origem ori where id_tipo_origem = 4 and 0=%s' + sql_exists + ' limit 100'
        else:
            sql = 'select ori.id_origem, ori.nm_origem from insta_origem ori where ori.id_origem_pai = %s' + sql_exists
        
        self.open()
        try:
            with self.connection.cursor() as cursor:                
                cursor.execute(sql, (source_hierarchy))
                results = cursor.fetchall()
        finally:
            self.connection.close()
        
        return results

    def searchPicture(self, url=None, to_post=False, all=False, to_model=False):
        '''Consultar imagem'''
        
        if to_model:
            sql = 'select f.ds_foto,f.nm_url_foto,f.dt_foto,f.nm_usuario_foto,f.qt_curtida_foto,f.dt_leitura,f.nm_tag,o.nm_origem, f.ic_repostado '
            sql += ' from insta_foto f inner join insta_origem o on o.id_origem = f.id_origem where nm_usuario_foto is not null and ic_imagem = 1'
        elif to_post:
            sql  = "select id_foto, nm_url_foto, nm_usuario_foto, ds_foto from insta_foto p where dt_foto < curdate()-INTERVAL 10 DAY and ic_repostado = 0 "
            sql += "and not exists (select 1 from insta_foto f where f.ic_repostado = 1 and f.dt_repostado > curdate() - INTERVAL 10 DAY and f.id_origem = p.id_origem) "
            sql += "and p.nm_usuario_foto != 'dogman800' and p.ic_imagem = 1 limit 1"
        elif all:
            sql = 'select id_foto, nm_url_foto, ds_foto, qt_curtida_foto, nm_tag from insta_foto where ic_repostado = 0 and ic_imagem = 1'
        elif url == None:            
            sql = 'select id_foto, nm_url_foto from insta_foto where nm_usuario_foto is null and ic_imagem = 1'
        else:
            sql = 'select id_foto, nm_url_foto from insta_foto where nm_url_foto = %s'            

        self.open()
        try:
            with self.connection.cursor() as cursor:                
                cursor.execute(sql, (url))
                results = cursor.fetchall()
        finally:
            self.connection.close()
        
        return results
    
    def searchPictureComment(self):
        '''Consultar imagem não comentada'''
        
        sql = 'select id_foto, nm_url_foto from insta_foto where ic_comentado = 0'
        
        self.open()
        try:
            with self.connection.cursor() as cursor:                
                cursor.execute(sql)
                results = cursor.fetchall()
        finally:
            self.connection.close()
        
        return results
    
    def updatePictureHistoric(self, lst_pic):
        self.open()
        try:
            with self.connection.cursor() as cursor:                
                sql = "update insta_foto set nm_usuario_foto = %s, qt_curtida_foto = %s, dt_foto = %s, ds_foto = %s, nm_tag = %s  where nm_url_foto = %s"
                cursor.executemany(sql, lst_pic)
                self.connection.commit()
        finally:
            self.connection.close()       
    
    def updatePictureComment(self, url, comment_date, text, like_date, comment=False, like=False):
        '''Atualizar quando uma imagem é comentada'''
        self.open()
        try:
            with self.connection.cursor() as cursor:                
                sql = "update insta_foto set ic_comentado = %s, dt_comentado = %s, ds_texto = concat(IFNULL(ds_texto,''''), ''-'', %s), ic_curtido = %s, dt_curtido = %s where nm_url_foto = %s"
                cursor.execute(sql, (str(int(comment)), comment_date, text, str(int(like)), like_date, url))
                self.connection.commit()
        finally:
            self.connection.close()        
            
    def updatePictureRepost(self, url, repost_date, text, repost=False):
        '''Atualizar quando uma imagem é repostada'''
        self.open()
        try:
            with self.connection.cursor() as cursor:                
                sql = "update insta_foto set ic_repostado = %s, dt_repostado = %s, ds_texto = concat(IFNULL(ds_texto,''''), ''-'', CONVERT(%s USING utf8))  where nm_url_foto = %s"
                cursor.execute(sql, (str(int(repost)), repost_date, text, url))
                self.connection.commit()
        finally:
            self.connection.close()
            
    def saveSourceHistory(self, post, follower, follow, source, is_private, read_date, genre, bio):
        '''Salvar dados da conta'''
        
        self.open()
        try:
            with self.connection.cursor() as cursor:               
                sql = 'insert into insta_origem_historico (id_origem, qt_seguidor, qt_seguindo, qt_publicacao, dt_leitura, ic_privado, sg_sexo, ds_biografia) values (%s, %s, %s, %s, %s, %s, %s, %s)'
                cursor.execute(sql, (source, follower, follow, post, read_date, str(int(is_private)), genre, bio))
                self.connection.commit()

        finally:
            self.connection.close()
            
    def searchPhrase(self, type_phrase):
        '''Consultar frase'''
        
        self.open()
        try:
            with self.connection.cursor() as cursor:                
                sql = 'select id_frase, ds_frase from insta_frase where id_tipo_origem = %s'
                cursor.execute(sql, (type_phrase.value))
                results = cursor.fetchall()
        finally:
            self.connection.close()
            
        return results
    
    def saveFollow(self, source, follow_date):
        '''Salvar seguidor'''
        self.open()
        try:
            with self.connection.cursor() as cursor:               
                sql = 'insert into insta_seguidor (id_origem, ic_seguindo, dt_seguindo) values (%s, 1, %s)'
                cursor.execute(sql, (source, follow_date))
                self.connection.commit()
        finally:
            self.connection.close()
    
    def searchFollow(self, to_train=True):
        '''Consultar usuários seguidos para treinar o ML'''
        
        sql = ''
        if to_train:
            sql = 'select seg.id_origem, ori.nm_origem, seg.dt_seguindo, pai.nm_origem as nm_pai, seg.dt_deseguindo, his.qt_publicacao, his.qt_seguidor, '
            sql += ' his.qt_seguindo, seg.ic_retorno, his.ic_privado, his.sg_sexo '
            sql += ' from insta_seguidor seg inner join insta_origem ori on ori.id_origem = seg.id_origem'
            sql += ' inner join insta_origem_historico his on his.id_origem = ori.id_origem'
            sql += ' inner join insta_origem pai on pai.id_origem = ori.id_origem_pai'
        else:
            sql = 'select ori.id_origem, ori.nm_origem, ppp.nm_origem as nm_pai, ori.id_origem_pai, his.qt_publicacao, his.qt_seguidor, '
            sql += ' his.qt_seguindo, his.ic_privado, his.sg_sexo'
            sql += ' from insta_origem ori inner join insta_origem_historico his on ori.id_origem = his.id_origem'
            sql += ' inner join insta_origem ppp on ori.id_origem_pai = ppp.id_origem'
            sql += ' where ori.id_tipo_origem = 4'
            sql += ' and not exists(select 1 from insta_seguidor seg where seg.id_origem = ori.id_origem) '
            sql += ' and his.ic_privado is not null'
        
        self.open()
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(sql)
                results = cursor.fetchall()
        finally:
            self.connection.close()            
        return results
    
    def saveUnfollow(self, source, unfollow_date):
        '''Salvar deseguidor'''
       
        self.open()
        try:
            with self.connection.cursor() as cursor:               
                sql = 'update insta_seguidor set ic_seguindo = 0, dt_deseguindo = %s where id_origem = %s'
                cursor.execute(sql, (unfollow_date, source))
                self.connection.commit()
        finally:
            self.connection.close()
            
    def searchFollower(self):
        '''Consultar seguidor'''
        self.open()
        try:
            with self.connection.cursor() as cursor:                
                #sql = 'select id_origem, nm_origem from insta_origem ori where ori.id_tipo_origem = 4'
                #sql += ' and not exists(select 1 from insta_seguidor seg where seg.id_origem = ori.id_origem) limit 30'
                sql = 'select id_origem, nm_origem, id_origem_pai '
                sql += ' from insta_origem ori  '
                sql += ' where ori.id_tipo_origem = 4 '
                sql += ' and not exists(select 1 from insta_seguidor seg where seg.id_origem = ori.id_origem) ' 
                sql += ' and not exists(select 1 from insta_seguidor seg inner join insta_origem pai on seg.id_origem = pai.id_origem '
                sql += ' where seg.dt_seguindo = (select max(dt_seguindo) from insta_seguidor) '
                sql += ' and pai.id_origem_pai = ori.id_origem_pai)  limit 50'
                
                cursor.execute(sql)
                results = cursor.fetchall()
        finally:
            self.connection.close()
        return results
    
    def searchUnfollower(self):
        '''Consultar seguidor para deseguir'''
        self.open()
        try:
            with self.connection.cursor() as cursor:                
                sql = 'select ori.id_origem, ori.nm_origem from insta_origem ori inner join insta_seguidor seg  on seg.id_origem = ori.id_origem '
                sql += ' where ori.id_tipo_origem = 4  and seg.ic_seguindo = 1 and dt_seguindo < curdate() - INTERVAL 5 DAY limit 60'
                cursor.execute(sql)
                results = cursor.fetchall()
        finally:
            self.connection.close()
        return results    
    
    def updatePictureValid(self, url, is_picture):
        '''Salvar deseguidor'''
       
        self.open()
        try:
            with self.connection.cursor() as cursor:               
                sql = 'update insta_foto set ic_imagem = %s where nm_url_foto = %s'
                cursor.execute(sql, (str(int(is_picture)), url))
                self.connection.commit()
        finally:
            self.connection.close()

    def saveBrewery(self, data):
        '''Salvar cervejarias'''
        self.open()
        try:
            with self.connection.cursor() as cursor:
                sql = 'insert ignore into untappd_cervejaria(id_cervejaria, nm_cervejaria, nm_facebook, nm_instagram, nm_cidade, nm_uf, cd_latitude, cd_longitude, nm_url)'
                sql += ' values( %s, %s, %s, %s, %s, %s, %s, %s, %s)'
                cursor.executemany(sql, data)
                self.connection.commit()
        finally:
            self.connection.close()
  
    def searchSource(self, source, type_source):
        '''Consultar a conta ou hashtag'''
        self.open()
        try:
            with self.connection.cursor() as cursor:
                sql = 'select id_origem, nm_origem from insta_origem where nm_origem = %s and id_tipo_origem = %s'
                cursor.execute(sql, (source, type_source.value))
                results = cursor.fetchall()             
        finally:
            self.connection.close()
        
        return results    
    
    def saveFollowBack(self, lst_user):
        
        format_string = ','.join(['%s'] * len(lst_user))        
        self.open()
        try:
            with self.connection.cursor() as cursor:
                sql = 'update insta_seguidor seg inner join insta_origem AS ori on seg.id_origem = ori.id_origem '
                sql += 'set seg.ic_retorno = 1 where ori.nm_origem in (%s)'
                cursor.execute(sql % format_string, tuple(lst_user))
                self.connection.commit()
        finally:
            self.connection.close()    
    
    def saveBeer(self, data):
        '''Salvar cervejas'''
        self.open()
        try:
            with self.connection.cursor() as cursor:
                sql = 'insert ignore into untappd_cerveja(id_cerveja, id_cervejaria, nm_cerveja, nm_estilo, pc_abv, nr_ibu, qt_checkin, nm_logo, nr_nota, dt_leitura)'
                sql += ' values( %s, %s, %s, %s, %s, %s, %s, %s, %s, curdate())'
                cursor.executemany(sql, data)
                self.connection.commit()
        finally:
            self.connection.close()
            
    def searchBeer(self):
        '''Consultar cervejas'''
        self.open()
        try:
            with self.connection.cursor() as cursor:
                sql = 'select id_cerveja, nm_cerveja, nr_ultima_pagina from untappd_cerveja'
                cursor.execute(sql)
                results = cursor.fetchall()             
        finally:
            self.connection.close()
        
        return results
    
    def saveUser(self, data):
        '''Salvar usuário'''
        self.open()
        try:
            with self.connection.cursor() as cursor:
                sql = 'insert ignore into untappd_usuario(id_usuario, nm_login, nm_usuario, nm_usuario_sobrenome, ds_biografia, nm_url_usuario, dt_leitura)'
                sql += ' values( %s, %s, %s, %s, %s, %s, curdate())'
                cursor.executemany(sql, data)
                self.connection.commit()
        finally:
            self.connection.close()
    
    
    def saveCheckIn(self, data):
        '''Salvar check-in'''
        self.open()
        try:
            with self.connection.cursor() as cursor:
                sql = 'insert ignore into untappd_checkin(id_usuario, id_cerveja, dt_checkin, nr_nota, ds_comentario, nm_localizacao, id_local, nm_local, nm_plataforma, nm_local_cidade, nm_local_uf, cd_local_latitude, cd_local_longitude, dt_leitura)'
                sql += ' values( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, curdate())'
                cursor.executemany(sql, data)
                self.connection.commit()
        finally:
            self.connection.close()
            
    def saveCheckInPage(self, page, beer_id):
        '''Salvar página do checkin da cerveja'''
        self.open()
        try:
            with self.connection.cursor() as cursor:
                sql = 'update untappd_cerveja set nr_ultima_pagina = %s where id_cerveja = %s'
                cursor.execute(sql, (page, beer_id))
                self.connection.commit()
        finally:
            self.connection.close()

            
    def searchUser(self):
        '''Consultar usuario'''
        self.open()
        try:
            with self.connection.cursor() as cursor:                
                sql = 'select us.id_usuario, us.nm_login, us.nr_ultima_pagina from untappd_usuario us where us.nr_ultima_pagina != 0'
                cursor.execute(sql)
                results = cursor.fetchall()             
        finally:
            self.connection.close()
            
        return results
            
    def saveInfoUser(self, data):
        '''Salvar informações adicionais do usuário'''
        self.open()
        try:
            with self.connection.cursor() as cursor:
                sql = "update untappd_usuario set qt_checkin = %s, qt_amigo = %s, qt_cerveja = %s, qt_seguidor = %s, qt_foto = %s, nm_url_foto = %s, nr_ultima_pagina = %s where id_usuario = %s"
                cursor.executemany(sql, data)
                self.connection.commit()
        finally:
            self.connection.close()
            
    def saveCheckInUserPage(self, page, user_id):
        '''Salvar página do checkin do usuário'''
        self.open()
        try:
            with self.connection.cursor() as cursor:
                sql = 'update untappd_usuario set nr_ultima_pagina = %s where id_usuario = %s'
                cursor.execute(sql, (page, user_id))
                self.connection.commit()
        finally:
            self.connection.close()
    
    def saveCheckInUser(self, data):
        self.open()
        try:
            with self.connection.cursor() as cursor:
                sql = 'insert ignore into untappd_checkin_usuario(id_checkin, id_cerveja, id_usuario, nm_estilo_cerveja, nm_cerveja, nm_cervejaria, id_local, dt_checkin)'
                sql += ' values( %s, %s, %s, %s, %s, %s, %s, %s)'
                cursor.executemany(sql, data)
                self.connection.commit()
        finally:
            self.connection.close()
