from urllib.request import urlopen
import urllib.error
import pandas as pd
import json
import requests
from pandas.io.json import json_normalize 
class Untappd():
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.url = 'https://api.untappd.com/v4/{}?client_id={}&client_secret={}'
        
    def searchBrewery(self, brewery_id):
        url_brewery = 'brewery/info/' + str(brewery_id)
        url_ = self.url.format(url_brewery,self.client_id, self.client_secret)
        brewery = json_normalize(json.loads(urlopen(url_).read().decode()))
        beer = json_normalize(brewery['response.brewery.beer_list.items'][0])
        brewery_ = beer[['total_count','beer.bid','beer.beer_name',
                    'beer.beer_label','beer.beer_style','beer.beer_abv',
                    'beer.beer_ibu','brewery.contact.facebook','brewery.contact.instagram',
                    'brewery.location.brewery_city','brewery.location.brewery_state',
                    'brewery.location.lat','brewery.location.lng']].rename({'total_count':'total_checkin',
                                                                         'beer.bid': 'id',
                                                                         'beer.beer_name' : 'cerveja',
                                                                         'beer.beer_label': 'logo',
                                                                         'beer.beer_style': 'estilo',
                                                                         'beer.beer_abv' : 'abv',
                                                                         'beer.beer_ibu' : 'ibu',
                                                                         'brewery.contact.facebook' : 'facebook',
                                                                         'brewery.contact.instagram' : 'instagram',
                                                                         'brewery.location.brewery_city' : 'cidade',
                                                                         'brewery.location.brewery_state' : 'uf',
                                                                         'brewery.location.lat' : 'latitude',
                                                                         'brewery.location.lng' : 'longitude'}, axis=1)
        brewery_.insert(0, 'cervejaria', brewery['response.brewery.brewery_name'].loc[0])
        brewery_.insert(0, 'url', brewery['response.brewery.brewery_page_url'].loc[0])
        brewery_.insert(0, 'cervejaria_id', brewery_id)
        brewery_['nota'] = None
        return brewery_
    
    def searchBeerRating(self, beer_id):
        url_beer = 'beer/info/' + str(beer_id)
        url_ = self.url.format(url_beer, self.client_id, self.client_secret)
        beer = json_normalize(json.loads(urlopen(url_).read().decode()))
        return beer['response.beer.weighted_rating_score'].loc[0]
    
    def searchBeerCheckIn(self, beer_id, max_page=None):
        def rename(data, next_page):        
            df = data[['user.uid','user.user_name','user.first_name',
                'user.last_name','rating_score','checkin_comment',
                'user.location','created_at','user.url',
                'user.bio','venue.venue_id','venue.venue_name',
                'toasts.total_count','comments.total_count','source.app_name',
                'venue.location.venue_city','venue.location.venue_state','venue.location.lat',
                'venue.location.lng']].rename({'user.uid': 'id_usuario',
                                               'user.user_name': 'usuario',
                                               'user.first_name': 'nome',
                                               'user.last_name': 'sobrenome',
                                               'rating_score': 'nota',
                                               'checkin_comment':'comentario',
                                               'user.location':'localizacao',
                                               'created_at':'data',
                                               'user.url':'url_usuario',
                                                'user.bio':'biografia',
                                               'venue.venue_id': 'local_id',
                                               'venue.venue_name':'local_nome',
                                                'toasts.total_count': 'total_avaliacao',
                                               'comments.total_count': 'total_comentario',
                                               'source.app_name':'plataforma',
                                                'venue.location.venue_city':'local_cidade',
                                               'venue.location.venue_state':'local_uf',
                                               'venue.location.lat':'local_lat',
                                                'venue.location.lng':'local_lng',}, axis=1)
            
            df.insert(0, 'proxima_pagina', next_page)
            return df

        url_beer = 'beer/checkins/' + str(beer_id)
        url_ = self.url.format(url_beer, self.client_id, self.client_secret)
        if max_page != None:
            url_ = url_ + '&max_id=' + str(max_page)

        try:
            
            check = json_normalize(json.loads(urlopen(url_).read().decode()))
            if len(check['response.checkins.items'][0]) > 0:        
                return rename(json_normalize(check['response.checkins.items'][0]), check['response.pagination.max_id'].loc[0])
        except urllib.error.HTTPError as e:
            if e.code == '400':
                print('São permitidas apenas 300 check ins.')
        
        return None
    
    def searchUser(self, username, max_page=None):
        def rename(data):
            data = data[['response.user.uid',
                         'response.user.stats.total_checkins','response.user.user_cover_photo',
                         'response.user.stats.total_friends','response.user.stats.total_beers',
                         'response.user.stats.total_created_beers','response.user.stats.total_followings',
                         'response.user.stats.total_photos','response.user.checkins.pagination.max_id',
                         'response.user.checkins.items']].rename({'response.user.uid':'id_usuario',
                                                                 'response.user.stats.total_checkins':'total_checkin',
                                                                 'response.user.user_cover_photo':'foto_capa',
                                                                 'response.user.stats.total_friends':'total_amigo',
                                                                 'response.user.stats.total_beers':'total_cerveja',
                                                                 'response.user.stats.total_created_beers':'total_cerveja_criada',
                                                                 'response.user.stats.total_followings': 'total_seguidores',
                                                                 'response.user.stats.total_photos':'total_foto',
                                                                 'response.user.checkins.pagination.max_id':'proxima_pagina',
                                                                 'response.user.checkins.items':'checkin_outro'}, axis=1)
            return data

        url_beer = 'user/info/' + username
        url_ = self.url.format(url_beer, self.client_id, self.client_secret)
        if max_page != None:
            url_ = url_ + '&max_id=' + str(max_page)
        
        try:
            data = urlopen(url_).read().decode()       
            return  rename(json_normalize(json.loads(data)))    
        
        except urllib.error.HTTPError as e:
            if e.code == '400':
                print('São permitidas apenas 300 check ins.')     
            else:
                raise Exception(e.reason)
        return None
    