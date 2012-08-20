#!/usr/bin/python
# -*- coding: utf-8 -*-
#/*
# *      Copyright (C) 2011 Silen
# *
# *
# *  This Program is free software; you can redistribute it and/or modify
# *  it under the terms of the GNU General Public License as published by
# *  the Free Software Foundation; either version 2, or (at your option)
# *  any later version.
# *
# *  This Program is distributed in the hope that it will be useful,
# *  but WITHOUT ANY WARRANTY; without even the implied warranty of
# *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# *  GNU General Public License for more details.
# *
# *  You should have received a copy of the GNU General Public License
# *  along with this program; see the file COPYING.  If not, write to
# *  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
# *  http://www.gnu.org/copyleft/gpl.html
# */
import re, os, urllib, urllib2, cookielib, time, random, sys
from time import gmtime, strftime
from urlparse import urlparse

import subprocess, ConfigParser

import xbmc, xbmcgui, xbmcplugin, xbmcaddon

Addon = xbmcaddon.Addon(id='plugin.video.seasonvar.ru')
xbmcplugin.setContent(int(sys.argv[1]), 'movies')
icon = xbmc.translatePath(os.path.join(Addon.getAddonInfo('path'),'icon.png'))
fcookies = xbmc.translatePath(os.path.join(Addon.getAddonInfo('path'), r'resources', r'data', r'cookies.txt'))

# load XML library
lib_path = os.path.join(Addon.getAddonInfo('path'), r'resources', r'lib')

sys.path.append(os.path.join(Addon.getAddonInfo('path'), r'resources', r'lib'))
from BeautifulSoup  import BeautifulSoup
import xppod

import HTMLParser
hpar = HTMLParser.HTMLParser()

h = int(sys.argv[1])

def showMessage(heading, message, times = 3000):
    xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")'%(heading, message, times, icon))

#---------- parameter/info structure -------------------------------------------
class Param:
    url             = ''
    genre           = ''
    genre_name      = ''
    country         = ''
    country_name    = ''
    is_season       = ''
    name            = ''
    img             = ''
    search          = ''
    history         = ''
    playlist        = ''

class Info:
    img         = ''
    url         = '*'
    title       = ''
    text        = ''
    director    = ''
    actors      = ''
    year        = ''
    country     = ''
    genre       = ''

#---------- get parameters -----------------------------------------------------
def Get_Parameters(params):
    #-- url
    try:    p.url = urllib.unquote_plus(params['url'])
    except: p.url = ''
    #-- img
    try:    p.img = urllib.unquote_plus(params['img'])
    except: p.img = ''
    #-- is season flag
    try:    p.is_season = urllib.unquote_plus(params['is_season'])
    except: p.is_season = ''
    #-- name
    try:    p.name = urllib.unquote_plus(params['name'])
    except: p.name = ''
    #-- genre
    try:    p.genre = urllib.unquote_plus(params['genre'])
    except: p.genre = 'all'
    try:    p.genre_name = urllib.unquote_plus(params['genre_name'])
    except: p.genre_name = 'Все'
    #-- country
    try:    p.country = urllib.unquote_plus(params['country'])
    except: p.country = 'all'
    try:    p.country_name = urllib.unquote_plus(params['country_name'])
    except: p.country_name = 'Все'
    #-- search
    try:    p.search = urllib.unquote_plus(params['search'])
    except: p.search = ''
    #-- history
    try:    p.history = urllib.unquote_plus(params['history'])
    except: p.history = ''
    #-- playlist url
    try:    p.playlist = urllib.unquote_plus(params['playlist'])
    except: p.playlist = ''
    #-----
    return p

#----------- get Header string ---------------------------------------------------
def Get_Header(par, count):

    if par.search == '':
        info  = 'Сериалов: ' + '[COLOR FF00FF00]'+ str(count) +'[/COLOR] | '
        info += 'Жанр: ' + '[COLOR FFFF00FF]'+ par.genre_name + '[/COLOR] | '
        info += 'Страна: ' + '[COLOR FFFFF000]'+ par.country_name + '[/COLOR]'
    else:
        info  = 'Поиск: ' + '[COLOR FF00FFF0]'+ par.search +'[/COLOR]'

    if info <> '':
        #-- info line
        name    = info
        i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode=EMPTY'
        #-- filter parameters
        u += '&genre=%s'%urllib.quote_plus(par.genre)
        u += '&genre_name=%s'%urllib.quote_plus(par.genre_name)
        u += '&country=%s'%urllib.quote_plus(par.country)
        u += '&country_name=%s'%urllib.quote_plus(par.country_name)
        xbmcplugin.addDirectoryItem(h, u, i, True)

    #-- genre
    if par.genre == 'all' and par.search == '' and par.history == '':
        name    = '[COLOR FFFF00FF]'+ '[ЖАНР]' + '[/COLOR]'
        i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode=GENRE'
        #-- filter parameters
        u += '&genre=%s'%urllib.quote_plus(par.genre)
        u += '&genre_name=%s'%urllib.quote_plus(par.genre_name)
        u += '&country=%s'%urllib.quote_plus(par.country)
        u += '&country_name=%s'%urllib.quote_plus(par.country_name)
        xbmcplugin.addDirectoryItem(h, u, i, True)

    #-- genre
    if par.country == 'all' and par.search == '' and par.history == '':
        name    = '[COLOR FFFFF000]'+ '[СТРАНА]' + '[/COLOR]'
        i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode=COUNTRY'
        #-- filter parameters
        u += '&genre=%s'%urllib.quote_plus(par.genre)
        u += '&genre_name=%s'%urllib.quote_plus(par.genre_name)
        u += '&country=%s'%urllib.quote_plus(par.country)
        u += '&country_name=%s'%urllib.quote_plus(par.country_name)
        xbmcplugin.addDirectoryItem(h, u, i, True)

    #-- search & history
    if par.country == 'all' and par.genre == 'all' and par.search == '' and par.history == '':
        name    = '[COLOR FF00FFF0]' + '[ПОИСК]' + '[/COLOR]'
        i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode=MOVIE'
        #-- filter parameters
        u += '&search=%s'%urllib.quote_plus('Y')
        xbmcplugin.addDirectoryItem(h, u, i, True)

        name    = '[COLOR FF00FF00]'+ '[ИСТОРИЯ]' + '[/COLOR]'
        i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode=MOVIE'
        #-- filter parameters
        u += '&history=%s'%urllib.quote_plus('Y')
        xbmcplugin.addDirectoryItem(h, u, i, True)

def Empty():
    return False

#---------- movie list ---------------------------------------------------------
def Movie_List(params):
    #-- get filter parameters
    par = Get_Parameters(params)

    # show search dialog
    if par.search == 'Y':
        skbd = xbmc.Keyboard()
        skbd.setHeading('Поиск сериалов.')
        skbd.doModal()
        if skbd.isConfirmed():
            SearchStr = skbd.getText().split(':')
            url = 'http://seasonvar.ru/autocomplete.php?query='+urllib.quote(SearchStr[0])
            par.search = SearchStr[0]
        else:
            return False
    else:
        url = 'http://seasonvar.ru/index.php?onlyjanrnew='+par.genre+'&&sortto=name&country='+par.country+'&nocache='+str(random.random())

    #== get movie list =====================================================
    post = None
    request = urllib2.Request(url, post)

    request.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)')
    request.add_header('Host',	'seasonvar.ru')
    request.add_header('Accept', '*/*')
    request.add_header('Accept-Language', 'ru-RU')
    request.add_header('Referer',	'http://seasonvar.ru')

    try:
        f = urllib2.urlopen(request)
    except IOError, e:
        if hasattr(e, 'reason'):
            xbmc.log('We failed to reach a server. Reason: '+ e.reason)
        elif hasattr(e, 'code'):
            xbmc.log('The server couldn\'t fulfill the request. Error code: '+ e.code)

    html = f.read()

    # -- parsing web page --------------------------------------------------
    count = 1
    list  = []

    if par.search != '':                                #-- parsing search page
        s = json.loads(html)
        count = len(s['suggestions'])
        if count < 1: return False

        for i in range(0, count):
            name = s['suggestions'][i].encode('utf-8')
            list.append({'title':name, 'url':'http://seasonvar.ru/'+s['data'][i], 'img': icon})
    else:                                               #-- parsing serial list
        soup = BeautifulSoup(html, fromEncoding="utf-8")
        # -- get number of serials
        try:
            count = len(soup.findAll('div', {'class':'betterTip'}))
        except:
            return False

        for rec in soup.findAll('div', {'class':'betterTip'}):
            list.append({'url'   : 'http://seasonvar.ru'+rec.find('a')['href'].encode('utf-8'),
                         'title' : rec.find('a').text.encode('utf-8'),
                         'img'   : 'http://cdn.seasonvar.ru/oblojka/'+rec['id'].replace('div','')+'.jpg'})

    #-- add header info
    Get_Header(par, count)

    #-- get movie info
    #try:
    for rec in list:
        i = xbmcgui.ListItem(rec['title'], iconImage=rec['img'], thumbnailImage=rec['img'])
        u = sys.argv[0] + '?mode=SERIAL'
        u += '&name=%s'%urllib.quote_plus(rec['title'])
        u += '&url=%s'%urllib.quote_plus(rec['url'])
        u += '&genre=%s'%urllib.quote_plus(par.genre)
        u += '&genre_name=%s'%urllib.quote_plus(par.genre_name)
        u += '&country=%s'%urllib.quote_plus(par.country)
        u += '&country_name=%s'%urllib.quote_plus(par.country_name)
        xbmcplugin.addDirectoryItem(h, u, i, True)
    #except:
    #    pass

    xbmcplugin.endOfDirectory(h)


#---------- serial info ---------------------------------------------------------
def Serial_Info(params):
    #-- get filter parameters
    par = Get_Parameters(params)
    #== get serial details =================================================
    url = par.url
    post = None
    request = urllib2.Request(url, post)

    request.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)')
    request.add_header('Host',	'seasonvar.ru')
    request.add_header('Accept', '*/*')
    request.add_header('Accept-Language', 'ru-RU')
    request.add_header('Referer',	'http://seasonvar.ru')

    try:
        f = urllib2.urlopen(request)
    except IOError, e:
        if hasattr(e, 'reason'):
            xbmc.log('We failed to reach a server. Reason: '+ e.reason)
        elif hasattr(e, 'code'):
            xbmc.log('The server couldn\'t fulfill the request. Error code: '+ e.code)

    html = f.read()
    # -- parsing web page --------------------------------------------------
    soup = BeautifulSoup(html, fromEncoding="windows-1251")

    # -- check if serial has seasons and provide season list
    if par.is_season == '' and len(soup.findAll('div', {'class':'full-news-2-content'})) > 0:
        #-- generate list of seasons
        for rec in soup.find('div', {'class':'full-news-2-content'}).findAll('a'):
            s_url   = 'http://seasonvar.ru'+rec['href']
            s_name  = rec.text.replace('>>>', '').replace(u'Сериал ', '')
            if s_name.find(u'сезон(') > -1:
                s_name = s_name.split(u'сезон(')[0]+u'сезон'
            s_name = s_name.encode('utf-8')
            s_id    = rec['href'].split('-')[1]
            s_image = 'http://cdn.seasonvar.ru/oblojka/'+s_id+'.jpg'

            i = xbmcgui.ListItem(s_name, iconImage=s_image, thumbnailImage=s_image)
            u = sys.argv[0] + '?mode=SERIAL'
            #-- filter parameters
            u += '&name=%s'%urllib.quote_plus(s_name)
            u += '&url=%s'%urllib.quote_plus(s_url)
            u += '&genre=%s'%urllib.quote_plus(par.genre)
            u += '&genre_name=%s'%urllib.quote_plus(par.genre_name)
            u += '&country=%s'%urllib.quote_plus(par.country)
            u += '&country_name=%s'%urllib.quote_plus(par.country_name)
            u += '&is_season=%s'%urllib.quote_plus('*')
            xbmcplugin.addDirectoryItem(h, u, i, True)
    else:
        #-- generate list of movie parts
        # -- get movie info
        for rec in soup.find('td', {'class':'td-for-content'}).findAll('p'):
            if len(rec.findAll('span', {'class':'videl'})) > 0:
                for j in str(rec).split('<br />'):
                    r = re.compile('<span class="videl">(.+?)<\/span>(.+?)<\/br>', re.MULTILINE|re.DOTALL).findall(str(j)+'</br>')
                    for s in r:
                        if s[0] == 'Жанр:':     mi.genre        = s[1].replace('</p>', '')
                        if s[0] == 'Страна:':   mi.country      = s[1].replace('</p>', '')
                        if s[0] == 'Вышел:':    mi.year         = s[1].replace('</p>', '')
                        if s[0] == 'Режисёр:':  mi.director     = s[1].replace('</p>', '')
                        if s[0] == 'Роли:':     mi.actors       = s[1].replace('</p>', '')
            else:
                mi.text = rec.text.encode('utf-8')

        mi.img = soup.find('td', {'class':'td-for-content'}).find('img')['src']

        # -- get serial parts info
        # -- mane of season
        i = xbmcgui.ListItem('[COLOR FFFFF000]'+par.name + '[/COLOR]', path='', thumbnailImage=icon)
        u = sys.argv[0] + '?mode=EMPTY'
        xbmcplugin.addDirectoryItem(h, u, i, False)

        # -- get list of season parts
        s_url = ''
        s_num = 0

        #---------------------------
        try:
            playlist, playlist_url = Get_PlayList(soup, url)
        except:
            Initialize()
            playlist, playlist_url = Get_PlayList(soup, url)

        for rec in playlist:
            for par in rec.replace('"','').split(','):
                if par.split(':')[0]== 'comment':
                    name = str(s_num+1) + ' серия' #par.split(':')[1]+' '
                if par.split(':')[0]== 'file':
                    s_url = par.split(':')[1]+':'+par.split(':')[2]
            s_num += 1

            i = xbmcgui.ListItem(name, path = urllib.unquote(s_url), thumbnailImage=mi.img) # iconImage=mi.img
            u = sys.argv[0] + '?mode=PLAY'
            u += '&url=%s'%urllib.quote_plus(s_url)
            u += '&name=%s'%urllib.quote_plus(name)
            u += '&img=%s'%urllib.quote_plus(mi.img)
            u += '&playlist=%s'%urllib.quote_plus(playlist_url)
            i.setInfo(type='video', infoLabels={    'title':       mi.title,
                                                    'cast' :       mi.actors,
                            						'year':        int(mi.year),
                            						'director':    mi.director,
                            						'plot':        mi.text,
                            						'genre':       mi.genre})
            i.setProperty('fanart_image', mi.img)
            #i.setProperty('IsPlayable', 'true')
            xbmcplugin.addDirectoryItem(h, u, i, False)

    xbmcplugin.endOfDirectory(h)

#---------- get genre list -----------------------------------------------------
def Genre_List(params):
    #-- get filter parameters
    par = Get_Parameters(params)

    #-- get generes
    url = 'http://seasonvar.ru'

    post = None
    request = urllib2.Request(url, post)

    request.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)')
    request.add_header('Host',	'seasonvar.ru')
    request.add_header('Accept', '*/*')
    request.add_header('Accept-Language', 'ru-RU')
    request.add_header('Referer',	'http://seasonvar.ru')

    try:
        f = urllib2.urlopen(request)
    except IOError, e:
        if hasattr(e, 'reason'):
            xbmc.log('We failed to reach a server. Reason: '+ e.reason)
        elif hasattr(e, 'code'):
            xbmc.log('The server couldn\'t fulfill the request. Error code: '+ e.code)

    html = f.read()

    # -- parsing web page ------------------------------------------------------
    soup = BeautifulSoup(html, fromEncoding="windows-1251")

    for rec in soup.find('select', {'id':'chkonlyjanr'}).findAll('option'):
        par.genre       = rec['value']
        par.genre_name  = rec.text.capitalize().encode('utf-8')

        i = xbmcgui.ListItem(par.genre_name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode=MOVIE'
        #-- filter parameters
        u += '&genre=%s'%urllib.quote_plus(par.genre)
        u += '&genre_name=%s'%urllib.quote_plus(par.genre_name)
        u += '&country=%s'%urllib.quote_plus(par.country)
        u += '&country_name=%s'%urllib.quote_plus(par.country_name)
        xbmcplugin.addDirectoryItem(h, u, i, True)

    xbmcplugin.endOfDirectory(h)

#---------- get country list -----------------------------------------------------
def Country_List(params):
    #-- get filter parameters
    par = Get_Parameters(params)

    #-- get generes
    url = 'http://seasonvar.ru'

    post = None
    request = urllib2.Request(url, post)

    request.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)')
    request.add_header('Host',	'seasonvar.ru')
    request.add_header('Accept', '*/*')
    request.add_header('Accept-Language', 'ru-RU')
    request.add_header('Referer',	'http://seasonvar.ru')

    try:
        f = urllib2.urlopen(request)
    except IOError, e:
        if hasattr(e, 'reason'):
            xbmc.log('We failed to reach a server. Reason: '+ e.reason)
        elif hasattr(e, 'code'):
            xbmc.log('The server couldn\'t fulfill the request. Error code: '+ e.code)

    html = f.read()

    # -- parsing web page ------------------------------------------------------
    soup = BeautifulSoup(html, fromEncoding="windows-1251")

    for rec in soup.find('select', {'id':'chkonlycountry'}).findAll('option'):
        par.country       = rec['value']
        par.country_name  = rec.text.capitalize().encode('utf-8')

        i = xbmcgui.ListItem(par.country_name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode=MOVIE'
        #-- filter parameters
        u += '&genre=%s'%urllib.quote_plus(par.genre)
        u += '&genre_name=%s'%urllib.quote_plus(par.genre_name)
        u += '&country=%s'%urllib.quote_plus(par.country)
        u += '&country_name=%s'%urllib.quote_plus(par.country_name)
        xbmcplugin.addDirectoryItem(h, u, i, True)

    xbmcplugin.endOfDirectory(h)

#-------------------------------------------------------------------------------

def PLAY(params):
    #-- get filter parameters
    par = Get_Parameters(params)

    # -- if requested continious play
    if Addon.getSetting('continue_play') == 'true':
        # create play list
        pl=xbmc.PlayList(1)
        pl.clear()
        # -- get play list
        post = None
        request = urllib2.Request(par.playlist, post)

        request.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)')
        request.add_header('Host',	'seasonvar.ru')
        request.add_header('Accept', '*/*')
        request.add_header('Accept-Language', 'ru-RU')
        request.add_header('Referer',	'http://seasonvar.ru')

        try:
            f = urllib2.urlopen(request)
        except IOError, e:
            if hasattr(e, 'reason'):
                xbmc.log('We failed to reach a server. Reason: '+ e.reason)
            elif hasattr(e, 'code'):
                xbmc.log('The server couldn\'t fulfill the request. Error code: '+ e.code)

        html = f.read()
        html = xppod.Decode(html)

        s_num = 0
        s_url = ''
        is_found = False

        for rec in re.compile('{(.+?)}', re.MULTILINE|re.DOTALL).findall(html.replace('{"playlist":[', '')):
            for item in rec.replace('"','').split(','):
                if item.split(':')[0]== 'comment':
                    name = str(s_num+1) + ' серия' #par.split(':')[1]+' '
                if item.split(':')[0]== 'file':
                    s_url = item.split(':')[1]+':'+item.split(':')[2]
                #-- add item to play list
                if s_url == par.url:
                    is_found = True

            if is_found:
                i = xbmcgui.ListItem(name, path = urllib.unquote(s_url), thumbnailImage=par.img)
                i.setProperty('IsPlayable', 'true')
                pl.add(s_url, i)
            s_num += 1

        xbmc.Player().play(pl)
    # -- play only selected item
    else:
        i = xbmcgui.ListItem(par.name, path = urllib.unquote(par.url), thumbnailImage=par.img)
        i.setProperty('IsPlayable', 'true')
        xbmcplugin.setResolvedUrl(h, True, i)

#-------------------------------------------------------------------------------

def unescape(text):
    try:
        text = hpar.unescape(text)
    except:
        text = hpar.unescape(text.decode('utf8'))

    try:
        text = unicode(text, 'utf-8')
    except:
        text = text

    return text

def get_url(url):
    return "http:"+urllib.quote(url.replace('http:', ''))

#-------------------------------------------------------------------------------  !!!
#---------- cleanup javac code -------------------------------------------------
def Java_CleanUP(html):
    html = re.sub(re.compile("/\*.*?\*/",re.DOTALL ) ,"" ,html)
    txt = ''
    for rec in html.split('\n'):
        s = rec.split('//')[0]
        txt += s+'\n'

    return txt

#---------- set cookies --------------------------------------------------------
def Get_Cookies(url): #soup):

    config = ConfigParser.ConfigParser()
    config.read(os.path.join(Addon.getAddonInfo('path'),'cookie.txt'))

    sec = 'www.seasonvar.ru'
    cookie = ''
    for op in config.options(sec):
        if config.get(sec, op) != 'null':
            cookie += op+'=';
            cookie += config.get(sec, op)+';'

    return cookie

#---------- get play list ------------------------------------------------------
def Get_PlayList(soup, parent_url):
    #-- get play list url
    for rec in soup.findAll('script', {'type':'text/javascript'}):
        if rec.text.find('swfobject.embedSWF') > -1:
            z = '{'+ re.compile('var flashvars = \{(.+?)\};', re.MULTILINE|re.DOTALL).findall(rec.text)[0]+'}'
            for r in z.split(','):
                if r.split(':')[0] == '"pl"':
                    html = r.split(':')[1].replace('"', '')

    url = 'http://seasonvar.ru/' + xppod.Decode(html)
    '''
    #-- get play list url
    for rec in soup.findAll('script', {'type':'text/javascript'}):
        if rec.text.find('swfobject.embedSWF') > -1:
            z = rec.text.replace('$.post("','[').replace('", {',']')
            urlx = re.compile('\$\.post\("(.+?)", \{"(.+?)":"(.+?)"\}', re.MULTILINE|re.DOTALL).findall(rec.text)
            url = 'http://seasonvar.ru/'+urlx[0][0]
            code1 = urlx[0][1]
            code2 = urlx[0][2]
            break

    values = {code1 : code2}
    post = urllib.urlencode(values)

    request = urllib2.Request(url, post)

    request.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)')
    request.add_header('Host',	'seasonvar.ru')
    request.add_header('Accept', '*/*')
    request.add_header('Accept-Language', 'ru-RU')
    request.add_header('Referer',	parent_url)
    request.add_header('Content-Type',	'application/x-www-form-urlencoded')
    request.add_header('Cookie',	Get_Cookies(parent_url))
    request.add_header('X-Requested-With',	'XMLHttpRequest')

    try:
        f = urllib2.urlopen(request)
    except IOError, e:
        if hasattr(e, 'reason'):
            xbmc.log('We failed to reach a server. Reason: '+ e.reason)
        elif hasattr(e, 'code'):
            xbmc.log('The server couldn\'t fulfill the request. Error code: '+ e.code)

    html = f.read()

    url = 'http://seasonvar.ru/' + xppod.Decode(html)
    '''

    # -- get play list
    post = None
    request = urllib2.Request(url, post)

    request.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)')
    request.add_header('Host',	'seasonvar.ru')
    request.add_header('Accept', '*/*')
    request.add_header('Accept-Language', 'ru-RU')
    request.add_header('Referer',	'http://seasonvar.ru')

    try:
        f = urllib2.urlopen(request)
    except IOError, e:
        if hasattr(e, 'reason'):
            xbmc.log('We failed to reach a server. Reason: '+ e.reason)
        elif hasattr(e, 'code'):
            xbmc.log('The server couldn\'t fulfill the request. Error code: '+ e.code)

    html = f.read()
    html = xppod.Decode(html)

    return re.compile('{(.+?)}', re.MULTILINE|re.DOTALL).findall(html.replace('{"playlist":[', '')), url

#-------------------------------------------------------------------------------
def Initialize():
    startupinfo = None
    if os.name == 'nt':
        prog = '"'+os.path.join(Addon.getAddonInfo('path'),'phantomjs.exe" --cookies-file="')+os.path.join(Addon.getAddonInfo('path'),'cookie.txt')+'" "'+os.path.join(Addon.getAddonInfo('path'),'seasonvar.js"')
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= 1
    else:
        prog = [os.path.join(Addon.getSetting('PhantomJS_Path'),'phantomjs'), '--cookies-file='+os.path.join(Addon.getAddonInfo('path'),'cookie.txt'), os.path.join(Addon.getAddonInfo('path'),'seasonvar.js')]

    try:
        process = subprocess.Popen(prog, stdin= subprocess.PIPE, stdout= subprocess.PIPE, stderr= subprocess.PIPE,shell= False, startupinfo=startupinfo)
        process.wait()
    except:
        xbmc.log('*** PhantomJS is not found or failed.')

#-------------------------------------------------------------------------------
def get_params(paramstring):
	param=[]
	if len(paramstring)>=2:
		params=paramstring
		cleanedparams=params.replace('?','')
		if (params[len(params)-1]=='/'):
			params=params[0:len(params)-2]
		pairsofparams=cleanedparams.split('&')
		param={}
		for i in range(len(pairsofparams)):
			splitparams={}
			splitparams=pairsofparams[i].split('=')
			if (len(splitparams))==2:
				param[splitparams[0]]=splitparams[1]
	return param


def Test(params):
    #-- get filter parameters
    par = Get_Parameters(params)
    #-- add header info
    Get_Header(par, 1)

    xbmcplugin.endOfDirectory(h)

#-------------------------------------------------------------------------------
params=get_params(sys.argv[2])

# get cookies from last session
cj = cookielib.FileCookieJar(fcookies)
hr  = urllib2.HTTPCookieProcessor(cj)
opener = urllib2.build_opener(hr)
urllib2.install_opener(opener)

p  = Param()
mi = Info()
#a,b,c = xppod.Correction(lib_path)
#eval(compile(a,b,c))

mode = None

#---------------------------------
#Test(params)

try:
	mode = urllib.unquote_plus(params['mode'])
except:
	mode = '$'

if mode == '$':
    Initialize()
    mode = 'MOVIE'

if mode == 'MOVIE':
	Movie_List(params)
elif mode == 'GENRE':
    Genre_List(params)
elif mode == 'COUNTRY':
    Country_List(params)
elif mode == 'SERIAL':
	Serial_Info(params)
elif mode == 'EMPTY':
    Empty()
elif mode == 'PLAY':
	PLAY(params)


