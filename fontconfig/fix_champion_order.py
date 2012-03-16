#!/usr/bin/python

# load as UTF8
import sys
if sys.getdefaultencoding() != 'utf-8':
	reload(sys)
	sys.setdefaultencoding('utf-8')

import os
from os import path
import re
import json
from pymongo import Connection

# fontconfig_de_DE.txt 
RE_SEARCH_FONTCONFIG = re.compile('fontconfig_(?P<lang>\w+_\w+).txt')
# tr "game_item_description_5000" = "TBD"
RE_SEARCH_INFO = re.compile('game_(?P<class>\w+)_(?P<key>\w+)_(?P<id>\w+)"\s*=\s*"(?P<value>[^"]+)"')

CHAMPIONS = (
'Annie',
'Olaf',
'Galio',
'TwistedFate',
'XinZhao',
'Urgot',
'Leblanc',
'Vladimir',
'FiddleSticks',
'Kayle',
'MasterYi',
'Alistar',
'Ryze',
'Sion',
'Sivir',
'Soraka',
'Teemo',
'Tristana',
'Warwick',
'Nunu',
'MissFortune',
'Ashe',	
'Tryndamere',
'Jax',
'Morgana',
'Zilean',
'Singed',
'Evelynn',
'Twitch',
'Karthus',
'Chogath',
'Amumu',
'Rammus',	
'Anivia',
'Shaco',
'DrMundo',	
'Sona',
'Kassadin',
'Irelia',
'Janna',	
'Gangplank',	
'Corki',
'Karma',
'Taric',
'Veigar',		
'Trundle',
'Swain',
'Caitlyn',
'Blitzcrank',
'Malphite',
'Katarina',
'Nocturne',
'Maokai',
'Renekton',
'JarvanIV',
'Orianna',
'WuKong',
'Brand',
'LeeSin',
'Vayne',
'Rumble',
'Cassiopeia',
'Skarner',
'Heimerdinger',
'Nasus',
'Nidalee',
'Udyr',
'Poppy',
'Gragas',
'Pantheon',
'Ezreal',
'Mordekaiser',
'Yorick',
'Akali',
'Kennen',
'Garen',
'Leona',
'Malzahar',
'Talon',
'Riven',
'KogMaw',
'Shen',
'Lux',	
'Xerath',
'Shyvana',
'Graves',
'Fizz',
'Volibear',
)

def print_usage():
	print """
Usage:
	fix_champion_order.py <input font config filename>
	"""

def main(argv):
	if len(argv)!=2:
		print_usage()
		return -1		
	
	filename = argv[1]
	if not path.exists(filename):
		print "File: '%s' not exists." % filename
		return -1
	
	f = None
	try:
		f = open(filename, 'r')
	except Exception, e:
		print e
		return -1
	
	while True:
		l = f.readline()
		
		if l=='':
			f.close()
			break

		m = RE_SEARCH_INFO.search(l)
		if m!=None:
			if m.group('class')=='character' and m.group('key')=='displayname' and m.group('id') in CHAMPIONS:
				l = 'tr "game_%s_%s_%s" = "%s"\r\n' % (m.group('class'), m.group('key'), m.group('id'), '(%s) %s' % (m.group('id'), m.group('value')))

		print l,
	return 0

	items = {}
	champs = {}
	spells = {}

	for fname in os.listdir('.'):

		m = RE_SEARCH_FONTCONFIG.search(fname)
		if m != None:
			lang = m.group('lang')
#			print 'Proc [%s] - %s' % (lang, fname)
			
			f = None
			try:
				f = open(fname, 'r')
			except Exception, e:
				print e
				continue

			while True:
				l = f.readline()
				if l=='':
					f.close()
					break
				m = RE_SEARCH_INFO.search(l)
				if m!=None:
					if m.group('class')=='item':
						iid = int(m.group('id'))
						item = None

						# create item if not exists
						if not items.has_key(iid):
							item = {"_id": iid, "displayname": {}, "description": {} }
							items[iid] = item
						else:
							item = items[iid]

						if item.has_key(m.group('key')):
							item[m.group('key')][lang] = m.group('value')
					elif m.group('class')=='character':
						cid = m.group('id')
						champ = None

						if not champs.has_key(cid):
							champ = {"_id": cid, "displayname": {}, "description": {}  }
							champs[cid] = champ
						else:
							champ = champs[cid]

						if champ.has_key(m.group('key')):
							champ[m.group('key')][lang] = m.group('value')
					elif m.group('class')=='spell':
						sid = m.group('id')
						if not sid.startswith('Summoner'):
							continue
						sid = sid.replace('Summoner', '')

						if not sid in spells:
							spell = {"_id": sid, "displayname": {}, "description": {}}
							spells[sid] = spell
						else:
							spell = spells[sid]
						if m.group('key') in spell:
							spell[m.group('key')][lang] = m.group('value')

	# save into local mongo db
	tmp_items = items.values()
	champs = champs.values()
	items = []
	runes = []
	spells = spells.values()

	for i in tmp_items:
		if i['_id']<5000:
			items.append(i)
		else:
			runes.append(i)

	conn = Connection()['lol']['items']

	import codecs
	ct = codecs.open('loltw_constant.py', 'w', 'utf-8')
	ct.write(codecs.BOM_UTF8)

	f = open('items.urls', 'w')
	ct.write('ITEM_NAME_LOOKUP={')
	for i in items:
		conn.save(i)
		f.write('url="http://na.leagueoflegends.com/sites/default/files/game_data/%s/content/item/%d.gif"\n' % (NA_VER, i['_id']))
		f.write('out="../../static/img/items/%d.gif"\n' % (i['_id']))
		f.write('create-dirs\n\n')

		ct.write("'%s': '%s'," % (i['_id'], i['displayname'].get('zh_TW')))
	f.close()
	ct.write('}\n')
		
	conn = Connection()['lol']['runes']
	f = open('runes.urls', 'w')
	ct.write('RUNE_NAME_LOOKUP={')
	for r in runes:
		conn.save(r)
		f.write('url="http://na.leagueoflegends.com/sites/default/files/game_data/%s/content/rune/%d.gif"\n' % (NA_VER, r['_id']))
		f.write('out="../../static/img/runes/%d.gif"\n' % (r['_id']))
		f.write('create-dirs\n\n')

		ct.write("'%s': '%s'," % (r['_id'], r['displayname'].get('zh_TW')))
	f.close()
	ct.write('}\n')
		
	conn = Connection()['lol']['champions']
	ct.write('CHAMPION_NAME_LOOKUP={')
	f = open('champions.urls', 'w')
	for c in champs:
		conn.save(c)
		if not 'displayname' in c:
			continue
		if not 'en_US' in c['displayname']:
			continue
			
		name = re.sub('[^A-Za-z]', '_', c['displayname']['en_US'])
		
		# temp fix for tw pics :-/
		if name=='Twisted_Fate':
			name='Twisted%20Fate'
		if name=='Miss_Fortune':
			name='Miss%20Fortune'
		if name=='Xin_Zhao':
			name='Xin%20Zhao'
		
		f.write('url="http://dl.garenanow.com/lol/loltw/web/upfile/champion/%s/champion_icon.jpg"\n' % name)
		f.write('out="../../static/img/champions/%s.jpg"\n' % (c['_id']))
		f.write('create-dirs\n\n')
		
		ct.write("'%s': '%s'," % (c['_id'], c['displayname'].get('zh_TW')))
	f.close()
	ct.write('}\n')

	ct.write('SUMMONER_SPELL_NAME_LOOKUP={')
	for s in spells:
		if not 'displayname' in s:
			continue
		if not 'en_US' in s['displayname']:
			continue

		ct.write("'%s': '%s'," % (s['_id'], s['displayname'].get('zh_TW')))
	ct.write('}\n')

	ct.close()
#	print json.dumps(items.values())	
#	print json.dumps(champs.values())

if __name__ == '__main__':
	main(sys.argv)
