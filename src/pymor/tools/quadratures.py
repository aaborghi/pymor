from __future__ import absolute_import, division, print_function

import numpy as np

class GaussQuadratures(object):
    '''Gauss quadrature on the interval [0, 1]'''

    @classmethod
    def maxpoints(cls):
        return len(cls.points)

    @classmethod
    def _determine_order(cls, order=None, npoints=None):
        assert order is not None or npoints is not None, ValueError('must specify "order" or "npoints"')
        assert order is None or npoints is None, ValueError('cannot specify "order" and "npoints"')
        if order is not None:
            assert 0 <= order <= cls.order_map.size - 1, ValueError('order {} not implmented'.format(order))
            p = cls.order_map[order]
        else:
            assert 1 <= npoints <= cls.orders.size, ValueError('not implemented with {} points'.format(npoints))
            p = npoints - 1
        return p
    
    @classmethod
    def quadrature(cls, order=None, npoints=None):
        '''returns tuple (P, W) where P is an array of Gauss points with corresponding weights W for
        the given integration order "order" or with "npoints" integration points
        '''
        p = cls._determine_order(order, npoints)
        return cls.points[p], cls.weights[p]
    
    @classmethod
    def iter_quadrature(cls, order=None, npoints=None):
        '''iterates over a quadrature tuple wise
        '''
        p = cls._determine_order(order, npoints)
        for i in xrange(len(cls.points[p])):
            yield (cls.points[p][i], cls.weights[p][i])

    # taken from RBMatlab ...

    orders = np.array([1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23])
    order_map = np.array([0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9, 10, 10, 11, 11])

    points = (
      np.array([.5]),

      np.array([.2113248654051871177454256097490212721761991243649365619906988367580111638485333271531423022071252374,
                .7886751345948128822545743902509787278238008756350634380093011632419888361514666728468576977928747626]),

      np.array([.1127016653792583114820734600217600389167078294708409173412426233886516908063020966480712623141326482,
                .5,
                .8872983346207416885179265399782399610832921705291590826587573766113483091936979033519287376858673518]),

      np.array([.694318442029737123880267555535952474521373101851411811921390395467352642524755671479188300577603474e-1,
                .3300094782075718675986671204483776563997120651145428237035230115894899847683814827610623597822225942,
                .6699905217924281324013328795516223436002879348854571762964769884105100152316185172389376402177774058,
                .9305681557970262876119732444464047525478626898148588188078609604532647357475244328520811699422396526]),

      np.array([.469100770306680036011865608503035174371740446187345685631188567281146025416565765294285052232288690e-1,
                .2307653449471584544818427896498955975163566965472200218988841864702644073161223544820981663747145342,
                .5,
                .7692346550528415455181572103501044024836433034527799781011158135297355926838776455179018336252854658,
                .9530899229693319963988134391496964825628259553812654314368811432718853974583434234705714947767711310]),

      np.array([.337652428984239860938492227530026954326171311438550875637251917366932495778999018618556300390370075e-1,
                .1693953067668677431693002024900473264967757178024149645927366470739082516964284495278567981267692718,
                .3806904069584015456847491391596440322906946849299893249093024177128625328621800788753877863713254342,
                .6193095930415984543152508608403559677093053150700106750906975822871374671378199211246122136286745658,
                .8306046932331322568306997975099526735032242821975850354072633529260917483035715504721432018732307282,
                .9662347571015760139061507772469973045673828688561449124362748082633067504221000981381443699609629925]),

      np.array([.254460438286207377369051579760743687996145311646911082256154480434683348225799295971346149860371380e-1,
                .1292344072003027800680676133596057964629261764293048699400223240162850626639097431035865838165683764,
                .2970774243113014165466967939615192683263089929503149368064783741026680933869371723358436551361267061,
                .5,
                .7029225756886985834533032060384807316736910070496850631935216258973319066130628276641563448638732939,
                .8707655927996972199319323866403942035370738235706951300599776759837149373360902568964134161834316236,
                .9745539561713792622630948420239256312003854688353088917743845519565316651774200704028653850139628620]),

      np.array([.198550717512318841582195657152635047858823828492739808641801113137875511282903577802805203683438658e-1,
                .1016667612931866302042230317620847815814141341920175839649148524803913471617634539264240363521370305,
                .2372337950418355070911304754053768254790178784398035711245714503637725896157193637380192999031840090,
                .4082826787521750975302619288199080096666210935435131088414057631503977628892289429419658881444383232,
                .5917173212478249024697380711800919903333789064564868911585942368496022371107710570580341118555616768,
                .7627662049581644929088695245946231745209821215601964288754285496362274103842806362619807000968159910,
                .8983332387068133697957769682379152184185858658079824160350851475196086528382365460735759636478629695,
                .9801449282487681158417804342847364952141176171507260191358198886862124488717096422197194796316561342]),

      np.array([.159198802461869550822118985481635649752975997540373352249883440754598128016996234690631253865529442e-1,
                .819844463366821028502851059651325617279466409376620019478140101802724965592049405530269014870712298e-1,
                .1933142836497048013456489803292629076071396975297176535635935288593663267544994007083799930482157077,
                .3378732882980955354807309926783316957140218696315134555864762615789067102324378754034506991507512164,
                .5,
                .6621267117019044645192690073216683042859781303684865444135237384210932897675621245965493008492487836,
                .8066857163502951986543510196707370923928603024702823464364064711406336732455005992916200069517842923,
                .9180155536633178971497148940348674382720533590623379980521859898197275034407950594469730985129287702,
                .9840801197538130449177881014518364350247024002459626647750116559245401871983003765309368746134470558]),

      np.array([.130467357414141399610179939577739732858650266538089403843939666517023983826819201871382175218657218e-1,
                .674683166555077446339516557882534757362284925173347737390201340773126224309722193216046355269771146e-1,
                .1602952158504877968828363174425632121153526440825952661675914055237207123024625376924607132147598102,
                .2833023029353764046003670284171079188999640811718767517486492434281165054611482493874486210249411394,
                .4255628305091843945575869994351400076912175702896541521460053732420481913221657393144111851002681544,
                .5744371694908156054424130005648599923087824297103458478539946267579518086778342606855888148997318456,
                .7166976970646235953996329715828920811000359188281232482513507565718834945388517506125513789750588606,
                .8397047841495122031171636825574367878846473559174047338324085944762792876975374623075392867852401898,
                .9325316833444922553660483442117465242637715074826652262609798659226873775690277806783953644730228854,
                .9869532642585858600389820060422260267141349733461910596156060333482976016173180798128617824781342782]),

      np.array([.108856709269715035980309994385713046142887955401077922870994670081681003095550058998403009163276150e-1,
                .564687001159523504624211153480363666841621243873428075162944722311943430713136662788547024367013129e-1,
                .1349239972129753379532918739844232709751784689869348440108108301564933774707403852022882945143581500,
                .2404519353965940920371371652706952227598864424400357554895386942566520367744635535872006099477254724,
                .3652284220238275138342340072995692376601890687804738591880371840599714668881526321480892038778663494,
                .5,
                .6347715779761724861657659927004307623398109312195261408119628159400285331118473678519107961221336506,
                .7595480646034059079628628347293047772401135575599642445104613057433479632255364464127993900522745276,
                .8650760027870246620467081260155767290248215310130651559891891698435066225292596147977117054856418500,
                .9435312998840476495375788846519636333158378756126571924837055277688056569286863337211452975632986871,
                .9891143290730284964019690005614286953857112044598922077129005329918318996904449941001596990836723850]),

      np.array([.92196828766403746547254549253595885199224000931342447686589390961033778408730088873713660547738821e-2,
                .479413718147625716607670669404519037312016453933512267229621196593826021353821047565152860881333661e-1,
                .1150486629028476564815530833935909620075371249905341811677904678754417284457643879917875003882890447,
                .2063410228566912763516487905297328598154507429759737592448645601663296503120523687821446175056258990,
                .3160842505009099031236542316781412193718199293322951893441000602479550352416060630606327857497267114,
                .4373832957442655422637793152680734350083015418472778633935391226257689718793051556285658507652543202,
                .5626167042557344577362206847319265649916984581527221366064608773742310281206948443714341492347456798,
                .6839157494990900968763457683218587806281800706677048106558999397520449647583939369393672142502732886,
                .7936589771433087236483512094702671401845492570240262407551354398336703496879476312178553824943741010,
                .8849513370971523435184469166064090379924628750094658188322095321245582715542356120082124996117109553,
                .9520586281852374283392329330595480962687983546066487732770378803406173978646178952434847139118666339,
                .9907803171233596253452745450746404114800775999068657552313410609038966221591269911126286339452261179])
      )

    weights = (
      np.array([1.000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000]),

      np.array([.5000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000,
                .5000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000]),

      np.array([.2777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777768,
              .4444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444,
              .2777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777]),

      np.array([.1739274225687269286865319746109997036176743479169467702462646597593759337329551758609918838661290805,
                .3260725774312730713134680253890002963823256520830532297537353402406240662670448241390081161338709199,
                .3260725774312730713134680253890002963823256520830532297537353402406240662670448241390081161338709201,
                .1739274225687269286865319746109997036176743479169467702462646597593759337329551758609918838661290798]),

      np.array([.1184634425280945437571320203599586813216300011062070077914139441108586442015215492899967152469757221,
                .2393143352496832340206457574178190964561477766715707699863638336669191335762562284877810625308020550,
                .2844444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444445,
                .2393143352496832340206457574178190964561477766715707699863638336669191335762562284877810625308020556,
                .1184634425280945437571320203599586813216300011062070077914139441108586442015215492899967152469757224]),

      np.array([.8566224618958517252014807108636644676341125074202199119931771989947288027117007732396385271319433505e-1,
                .1803807865240693037849167569188580558307609463733727411448696201185700189186308591604811009944096747,
                .2339569672863455236949351719947754974058278028846052676558126599819571008101990635155550462923959909,
                .2339569672863455236949351719947754974058278028846052676558126599819571008101990635155550462923959910,
                .1803807865240693037849167569188580558307609463733727411448696201185700189186308591604811009944096740,
                .8566224618958517252014807108636644676341125074202199119931771989947288027117007732396385271319433505e-1]),

      np.array([.6474248308443484663530571633954100916429370112997333198860431936232761748602115435781270908146042335e-1,
                .1398526957446383339507338857118897912434625326132993822685070163468094052152813384066204714505988094,
                .1909150252525594724751848877444875669391825417669313673755417255153527732170648541743423296720224005,
                .2089795918367346938775510204081632653061224489795918367346938775510204081632653061224489795918367346,
                .1909150252525594724751848877444875669391825417669313673755417255153527732170648541743423296720224007,
                .1398526957446383339507338857118897912434625326132993822685070163468094052152813384066204714505988092,
                .6474248308443484663530571633954100916429370112997333198860431936232761748602115435781270908146042285e-1]),

      np.array([.5061426814518812957626567715498109505769704552584247852950184903237008938173539243014136965202250520e-1,
                .1111905172266872352721779972131204422150654350256247823629546446468084072852245204268265711885989640,
                .1568533229389436436689811009933006566301644995013674688451319725374781359710867484808490381169642782,
                .1813418916891809914825752246385978060970730199471652702624115337833433673619533386621830210424142548,
                .1813418916891809914825752246385978060970730199471652702624115337833433673619533386621830210424142549,
                .1568533229389436436689811009933006566301644995013674688451319725374781359710867484808490381169642781,
                .1111905172266872352721779972131204422150654350256247823629546446468084072852245204268265711885989639,
                .5061426814518812957626567715498109505769704552584247852950184903237008938173539243014136965202250335e-1]),

      np.array([.4063719418078720598594607905526182533783086039120537535555383844034334315422603147278927735147128571e-1,
                .9032408034742870202923601562145640475716891086602024224916795323567864527247313488229748865159985275e-1,
                .1303053482014677311593714347093164248859201022186499759699985010598054078344456223238230465475087002,
                .1561735385200014200343152032922218327993774306309523227770055827995719486620096582850609609440031770,
                .1651196775006298815822625346434870244394053917863441672965482489292013101536911060720584530108339632,
                .1561735385200014200343152032922218327993774306309523227770055827995719486620096582850609609440031768,
                .1303053482014677311593714347093164248859201022186499759699985010598054078344456223238230465475087008,
                .9032408034742870202923601562145640475716891086602024224916795323567864527247313488229748865159985195e-1,
                .4063719418078720598594607905526182533783086039120537535555383844034334315422603147278927735147128848e-1]),

      np.array([.3333567215434406879678440494666589642893241716007907256434744080670603204204355088839275484252944050e-1,
                .7472567457529029657288816982884866620127831983471368391773863437661932736331500547297363231736597515e-1,
                .1095431812579910219977674671140815962293859352613385449404782718175999553264756406213419965886010958,
                .1346333596549981775456134607847346764298799692304418979002816381210767161595896383821133183546263805,
                .1477621123573764350869464973256691647105233585134268006771540148779979691085761646351782978968771084,
                .1477621123573764350869464973256691647105233585134268006771540148779979691085761646351782978968771085,
                .1346333596549981775456134607847346764298799692304418979002816381210767161595896383821133183546263804,
                .1095431812579910219977674671140815962293859352613385449404782718175999553264756406213419965886010963,
                .7472567457529029657288816982884866620127831983471368391773863437661932736331500547297363231736597595e-1,
                .3333567215434406879678440494666589642893241716007907256434744080670603204204355088839275484252943861e-1]),

      np.array([.2783428355808683324137686022127428936425781284844907417419214283707770364036877194184561103615942288e-1,
                .6279018473245231231734714961197005009880789569770175033196700540895728756623563881734382085702726505e-1,
                .9314510546386712571304882071582794584564237402010170589075320208693617400439275123466537925898979300e-1,
                .1165968822959952399592618524215875697158990861584792545136598610609661066094404979770199742191308422,
                .1314022722551233310903444349452545976863823388015722781900276857427564016697726267762084985085133530,
                .1364625433889503153572417641681710945780209849473918737988002057266126530195794265058334322403586472,
                .1314022722551233310903444349452545976863823388015722781900276857427564016697726267762084985085133529,
                .1165968822959952399592618524215875697158990861584792545136598610609661066094404979770199742191308422,
                .9314510546386712571304882071582794584564237402010170589075320208693617400439275123466537925898979305e-1,
                .6279018473245231231734714961197005009880789569770175033196700540895728756623563881734382085702726505e-1,
                .2783428355808683324137686022127428936425781284844907417419214283707770364036877194184561103615942288e-1]),

      np.array([.2358766819325591359730798074250853015851453699742354478025267350190486057601935533541295353770726794e-1,
                .5346966299765921548012735909699811210728508673516244000256302105140949681374878827026865904815822880e-1,
                .8003916427167311316732626477167953593600586524543208895494977207897711258664557534082827631852886530e-1,
                .1015837133615329608745322279048991882532590736372950731992972828988228162552364218975721975323026162,
                .1167462682691774043804249494624390281297049860998774373652617489107460000397058376403395132542818452,
                .1245735229067013925002812180214756054152304512848094156976755015581397137286440215155784003090211766,
                .1245735229067013925002812180214756054152304512848094156976755015581397137286440215155784003090211766,
                .1167462682691774043804249494624390281297049860998774373652617489107460000397058376403395132542818452,
                .1015837133615329608745322279048991882532590736372950731992972828988228162552364218975721975323026162,
                .8003916427167311316732626477167953593600586524543208895494977207897711258664557534082827631852886530e-1,
                .5346966299765921548012735909699811210728508673516244000256302105140949681374878827026865904815822885e-1,
                .2358766819325591359730798074250853015851453699742354478025267350190486057601935533541295353770726794e-1])
      )
