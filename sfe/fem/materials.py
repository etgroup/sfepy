from sfe.base.base import *

##
# 21.07.2006, c
class Materials( Container ):
    ##
    # 24.07.2006, c
    def fromConf( conf, wanted = None ):

        if wanted is None:
            wanted = conf.keys()

        objs = OneTypeList( Material )
        for key, val in conf.iteritems():
            if key in wanted:
                objs.append( Material( **val ) )
        obj = Materials( objs )
        return obj
    fromConf = staticmethod( fromConf )

    ##
    # 22.08.2006, c
    def setupRegions( self, regions ):
        for mat in self:
            mat.setupRegions( regions )

    ##
    # 01.08.2006, c
    # 29.10.2007
    def timeUpdate( self, ts, funmod, domain, extraMatArgs = None ):
        extraMatArgs = getDefault( extraMatArgs, {} )
        for mat in self:
            extraArgs = extraMatArgs.setdefault( mat.name, {} )
            mat.timeUpdate( ts, funmod, domain, **extraArgs )

    ##
    # 22.08.2006, c
    def setCurrentGroup( self, ig ):
        for mat in self:
            mat.setCurrentGroup( ig )

##
# 21.07.2006, c
class Material( Struct ):
    ##
    # 22.08.2006, c
    def __init__( self, **kwargs ):
        kwargs.setdefault( 'extraArgs', {} )
        Struct.__init__( self, **kwargs )

        self.regionName = self.region
        self.region = None
            
    ##
    # 22.08.2006, c
    def setupRegions( self, regions ):
        region = regions[self.regionName]
        self.igs = region.igs
        self.region = region 

    ##
    # 01.08.2006, c
    # 02.08.2006
    # 22.08.2006
    # 22.02.2007
    # 14.03.2007
    # 01.08.2007
    # 05.10.2007
    # 29.10.2007
    def timeUpdate( self, ts, funmod, domain, **extraArgs ):
        """coor is in region.vertices[ig] order (i.e. sorted by node number)"""
        if self.mode == 'function':
            self.datas = []

            if isinstance( self.function, str ):
                fun = getattr( funmod, self.function )
            else:
                fun = self.function

            kwargs = copy( self.extraArgs )
            kwargs.update( extraArgs )
            args = dict( ts = ts, region = self.region, **kwargs )

            for ig in self.igs:
                coor = domain.getMeshCoors()[self.region.getVertices( ig )]
                args.update( {'coor' : coor, 'ig' : ig} )
                self.datas.append( fun( **args ) )
            self.data = None

    ##
    # 31.07.2007, c
    def setData( self, datas ):
        self.mode = 'user'
        self.datas = datas
        self.data = None

    ##
    # 01.08.2007, c
    def setFunction( self, function ):
        self.mode =  'function'
        self.function = function

    ##
    # 01.08.2007, c
    def setExtraArgs( self, extraArgs ):
        self.extraArgs = extraArgs
        
    ##
    # 22.08.2006, c
    # 22.02.2007
    # 31.07.2007
    def setCurrentGroup( self, ig ):
        if (self.mode == 'function') or (self.mode == 'user'):
            try:
                ii = self.igs.index( ig )
                self.data = self.datas[ii]
            except:
                self.data = None

    ##
    # c: 02.08.2006, r: 01.02.2008
    def getData( self, regionName, ig, name = None ):
        """Returns None in function mode if setCurrentGroup() was not called."""
##         print 'getting', name

        if self.mode == 'here':
            if name is None:
                return self
            else:
                return nm.asarray( getattr( self, name ) )

        else:
            ii = self.igs.index( ig )
            if name is None:
                return self.datas[ii]
            else:
                return self.datas[ii][name]

    ##
    # 01.08.2007, c
    def reduceOnDatas( self, reduceFun, init = 0.0 ):
        out = {}.fromkeys( self.datas[0].keys(), init )

        for data in self.datas:
            for key, val in data.iteritems():
                out[key] = reduceFun( out[key], val )

        return out
