from idiokit import threado, util
from abusehelper.core import utils, cymru, bot, events
import urllib2,csv
class MDLBot2(bot.PollingBot):
	use_cymru_whois = bot.BoolParam(default=False)
	
	def augment(self):
		if not self.use_cymru_whois:
			return bot.PollingBot.augment(self)
		return cymru.CymruWhois() | self.printer()

	@threado.stream
	def printer(inner,self):
		i = 0
		while True:
			event = yield inner
			print i, event
			new = events.Event()
			new.update('ip',event.values('ip'))
			new.update('cc',event.values('cc'))
			new.update('asn', event.values('asn'))
			new.update('as name', event.values('as name'))
			inner.send(new)
			i += 1
    
	@threado.stream
	def poll(inner, self, url="http://www.malwaredomainlist.com/mdlcsv.php"):
#		url = "http://www.malwaredomainlist.com/hostslist/ip.txt"
		url = "http://www.malwaredomainlist.com/updatescsv.php"
		self.log.info("Downloading MDL active sites list")
		fileobj = urllib2.urlopen("http://www.malwaredomainlist.com/mdlcsv.php").readlines()
#		try:
#			info, fileobj = yield inner.sub(utils.fetch_url(url))
#			print info, fileobj.read()
#		except utils.FetchUrlFailed, fuf:
#			self.log.error("MDL active sites downloading failed: %r", fuf)
#			return
		self.log.info("MDL IP-list downloaded")
		
#		charset = info.get_param("charset")
		
#		if charset is None:
#			decode = util.guess_encoding
#		else:
#			decode = lambda x: x.decode(charset)
		
		# date,domain,ip,reverse,description,registrant,asn,inactive,country
		
		columns = ["date", "url", "ip", "reverse", "description", "registrant", "asn", "inactive", "cc"]


		lines = csv.DictReader(fileobj,columns)
		charset = 'utf-8'
		for line in lines:
			event = events.Event()
			for k,v in line.iteritems():
				try:
					event.add(k.decode(charset),v.decode(charset))
				except UnicodeDecodeError,e:
					self.log.info('Can not decode %s=%s' % (k,v))
					continue
			inner.send(event)
			print event
		inner.finish()


if __name__ == "__main__":
	MDLBot2.from_command_line().execute()
