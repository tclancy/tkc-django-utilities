from django.conf import settings
from django.db import models
from django.template.defaultfilters import slugify


class NameAndSlug(models.Model):
    '''
    convenience model for things that are just names
    '''
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200)
    
    def __unicode__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        """
        Slugify name if it doesn't exist. IMPORTANT: doesn't check to see
        if slug is a dupe!
        """
        if not self.slug:
            self.slug = slugify(self.name)
        super(NameAndSlug, self).save()
    
    class Meta:
        abstract = True
        ordering = ['name',]


class LiveManager(models.Manager):
    def get_query_set(self):
        return super(LiveManager, self).get_query_set().filter(active=True)


class ParentChildManager(models.Manager):
    def top_level_members(self):
        return super(ParentChildManager, self).get_query_set().filter(
            parent__isnull=True)


class LocationManager(models.Manager):
    def nearby_locations_by_zip(self, obj_table_name, zip_table_name, radius,
                         zip_code=None, lat=None, lng=None, 
                         max_results=100, use_miles=True):
        """
        Given a zip code (or lat/ long pair) and a radius, find all model objects
        inside the area. Pass the name of the object table and the
        name of the zip code table to create the join
        
        TODO: these have nasty SQL injection vulnerabilities due to me not
        wanting to fight with the dynamic names vs parameter insertion and just
        hacking them together. Need to revise, split out the table name replacement
        and move to parameters.
        """
        if use_miles:
            distance_unit = 3959
        else:
            distance_unit = 6371
        
        if not radius:
            radius = settings.DEFAULT_SEARCH_RADIUS
        
        from django.db import connection, transaction
        cursor = connection.cursor()
        if zip_code:
            cursor.execute("SELECT z.longitude, z.latitude FROM " + zip_table_name
                           + " z WHERE z.zip_code = %s", [zip_code])
            row = cursor.fetchone()
            cursor.close()
            if not row:
                return None
            lng = row[0]
            lat = row[1]
        else:
            if not lat or not lng:
                return None
        
        sql = """SELECT objs.*, (%f * acos( cos( radians(%f) )
        * cos( radians( latitude ) ) *
        cos( radians( longitude ) - radians(%f) )
        + sin( radians(%f) ) * sin( radians( latitude ) ) ) )
        AS distance FROM """ + zip_table_name + """ zips
        INNER JOIN """ + obj_table_name + """ objs
        ON zips.zip_code = objs.zip_code
        WHERE objs.active = 1
        HAVING distance < %d
        ORDER BY distance LIMIT 0 , %d;"""
        sql = sql  % (distance_unit, lat, lng, lat, int(radius), max_results)
        return super(LocationManager, self).raw(sql)
    
    def nearby_locations(self, obj_table_name, radius, lat=None, lng=None, 
                         max_results=100, use_miles=True):
        """
        Given a lat/ long pair and a radius, find all model objects
        inside the area. Pass the name of the object table to query
        """
        if use_miles:
            distance_unit = 3959
        else:
            distance_unit = 6371
        
        if not radius:
            radius = settings.DEFAULT_SEARCH_RADIUS
        
        from django.db import connection, transaction
        cursor = connection.cursor()
        
        sql = """SELECT objs.*, (%f * acos( cos( radians(%f) )
        * cos( radians( latitude ) ) *
        cos( radians( longitude ) - radians(%f) )
        + sin( radians(%f) ) * sin( radians( latitude ) ) ) )
        AS distance FROM """ + obj_table_name + """ objs
        HAVING distance < %d
        ORDER BY distance LIMIT 0 , %d;"""
        sql = sql % (distance_unit, lat, lng, lat, int(radius), max_results)
        return super(LocationManager, self).raw(sql)
