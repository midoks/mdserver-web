--[[
	a lua interface (build with luajit ffi) for  maxminddb to get country code from ip address
]]

local json				= 	require('cjson');  
local json_encode	    =	json.encode
local json_decode		=	json.decode
local ht_print			=	ngx.print
local ngx_log         	=   ngx.log
local ngx_ERR         	=   ngx.ERR
local ngx_CRIT			=   ngx.CRIT
local ngx_INFO			=   ngx.INFO

local ngx_sub				=	ngx.re.sub;
local ngx_gsub				=	ngx.re.gsub;
local ngx_unescape_uri		=	ngx.unescape_uri
local ngx_find				=	ngx.re.find
local string_sub			=	string.sub
local string_len			=	string.len
local string_byte			=	string.byte
local ngx_read_body			=	ngx.req.read_body
local ngx_decode_base64		=	ngx.decode_base64
local ngx_now 				=	ngx.now
local ngx_exit 				=	ngx.exit


 
 

local ffi = require 'ffi'
local ffi_new = ffi.new
local ffi_str = ffi.string
local ffi_copy = ffi.copy
local ffi_cast = ffi.cast

ffi.cdef[[

typedef unsigned int mmdb_uint128_t __attribute__ ((__mode__(TI)));

typedef struct MMDB_entry_s {
    struct MMDB_s *mmdb;
    uint32_t offset;
} MMDB_entry_s;

typedef struct MMDB_lookup_result_s {
    bool found_entry;
    MMDB_entry_s entry;
    uint16_t netmask;
} MMDB_lookup_result_s;

typedef struct MMDB_entry_data_s {
    bool has_data;
    union {
        uint32_t pointer;
        const char *utf8_string;
        double double_value;
        const uint8_t *bytes;
        uint16_t uint16;
        uint32_t uint32;
        int32_t int32;
        uint64_t uint64;
        mmdb_uint128_t uint128;
        bool boolean;
        float float_value;
    };

    uint32_t offset;
    uint32_t offset_to_next;
    uint32_t data_size;
    uint32_t type;
} MMDB_entry_data_s;

typedef struct MMDB_entry_data_list_s {
    MMDB_entry_data_s entry_data;
    struct MMDB_entry_data_list_s *next;
} MMDB_entry_data_list_s;

typedef struct MMDB_description_s {
    const char *language;
    const char *description;
} MMDB_description_s;

typedef struct MMDB_metadata_s {
    uint32_t node_count;
    uint16_t record_size;
    uint16_t ip_version;
    const char *database_type;
    struct {
        size_t count;
        const char **names;
    } languages;
    uint16_t binary_format_major_version;
    uint16_t binary_format_minor_version;
    uint64_t build_epoch;
    struct {
        size_t count;
        MMDB_description_s **descriptions;
    } description;
} MMDB_metadata_s;

typedef struct MMDB_ipv4_start_node_s {
    uint16_t netmask;
    uint32_t node_value;
} MMDB_ipv4_start_node_s;

typedef struct MMDB_s {
    uint32_t flags;
    const char *filename;
    ssize_t file_size;
    const uint8_t *file_content;
    const uint8_t *data_section;
    uint32_t data_section_size;
    const uint8_t *metadata_section;
    uint32_t metadata_section_size;
    uint16_t full_record_byte_size;
    uint16_t depth;
    MMDB_ipv4_start_node_s ipv4_start_node;
    MMDB_metadata_s metadata;
} MMDB_s;

typedef  char * pchar;

MMDB_lookup_result_s MMDB_lookup_string(MMDB_s *const mmdb,   const char *const ipstr, int *const gai_error,int *const mmdb_error);
int MMDB_open(const char *const filename, uint32_t flags, MMDB_s *const mmdb);
int MMDB_aget_value(MMDB_entry_s *const start,  MMDB_entry_data_s *const entry_data,  const char *const *const path);
char *MMDB_strerror(int error_code);
]]

local MMDB_SUCCESS				=	0
local MMDB_DATA_TYPE_POINTER	=	1
local MMDB_DATA_TYPE_UTF8_STRING=	2
local MMDB_DATA_TYPE_DOUBLE		=	3
local MMDB_DATA_TYPE_BYTES		=	4


-- you should install the libmaxminddb to your system
local maxm 	= ffi.load('{$WAF_ROOT}/mmdb/lib/libmaxminddb.so')
--https://github.com/maxmind/libmaxminddb


local _M	={}

local mt = { __index = _M }

function _M.new(maxmind_country_geoip2_file)
	 
	local mmdb 	=	ffi_new('MMDB_s') 
	local file_name_ip2   = ffi_new('char[?]',#maxmind_country_geoip2_file,maxmind_country_geoip2_file)
	local maxmind_reday   = maxm.MMDB_open(file_name_ip2,0,mmdb)
 
	return setmetatable({ mmdb=mmdb }, mt);
end



function _M:lookup(ip)

  	local ip_str  		= 	ffi_cast('const char *',ffi_new('char[?]',#ip+1,ip))
  	local gai_error  	=	ffi_new('int[1]')
	local mmdb_error	= 	ffi_new('int[1]')

	local result 		=	maxm.MMDB_lookup_string(self.mmdb,ip_str,gai_error,mmdb_error)

  	if mmdb_error[0] ~= MMDB_SUCCESS then
		return nil,'fail when lookup'
  	end

  	if gai_error[0] ~= MMDB_SUCCESS then
		return nil,'ga error'
	end


  	if true~=result.found_entry then
        ngx_log(ngx_ERR, "stream lua mmdb lookup: entry not found")
        return nil,'not found'
	end

	local lookup  		= 	ffi_new('const char*[3]') 
	lookup[0]			=	ffi_cast('const char *',ffi_new('char[?]',8,'country'))
	lookup[1]			=	ffi_cast('const char *',ffi_new('char[?]',9,'iso_code'))
	
	
	local entry_data  	= 	ffi_new('MMDB_entry_data_s[1]') 
	lookup   			= 	ffi_cast('const char *const *const',lookup)
	local mmdb_error 	= 	maxm.MMDB_aget_value(result.entry, entry_data, lookup);
 
	if mmdb_error ~= MMDB_SUCCESS then
		return nil,'no value'
	end

  	if true ~= entry_data[0].has_data  then
         ngx_log(ngx_ERR, "stream lua mmdb lookup: entry has no data")
         return nil,'no data'
    end
 
  	local country		=	''
	if entry_data[0].type == MMDB_DATA_TYPE_UTF8_STRING then
		return ffi_str(entry_data[0].utf8_string,entry_data[0].data_size) 
	end
	
	if entry_data[0].type ==MMDB_DATA_TYPE_BYTES then
    	return ffi_str(ffi_cast('char * ',entry_data[0].bytes),entry_data[0].data_size) 
	end

	return nil,'no data'
end
 
-- https://www.maxmind.com/en/geoip2-databases  you should download  the mmdb file from maxmind


function _M:get_area_code(ip)

  	local succ,country,err 	=	pcall(self.lookup,self,ip)
	 
	if succ==true then
		return country
	else
		return nil,err
	end
end

 
return _M;