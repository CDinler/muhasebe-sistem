<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="2.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
				xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
				xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
				xmlns:ccts="urn:un:unece:uncefact:documentation:2"
				xmlns:clm54217="urn:un:unece:uncefact:codelist:specification:54217:2001"
				xmlns:clm5639="urn:un:unece:uncefact:codelist:specification:5639:1988"
				xmlns:clm66411="urn:un:unece:uncefact:codelist:specification:66411:2001"
				xmlns:clmIANAMIMEMediaType="urn:un:unece:uncefact:codelist:specification:IANAMIMEMediaType:2003"
				xmlns:fn="http://www.w3.org/2005/xpath-functions" xmlns:link="http://www.xbrl.org/2003/linkbase"
				xmlns:n1="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
				xmlns:qdt="urn:oasis:names:specification:ubl:schema:xsd:QualifiedDatatypes-2"
				xmlns:udt="urn:un:unece:uncefact:data:specification:UnqualifiedDataTypesSchemaModule:2"
				xmlns:xbrldi="http://xbrl.org/2006/xbrldi" xmlns:xbrli="http://www.xbrl.org/2003/instance"
				xmlns:xdt="http://www.w3.org/2005/xpath-datatypes" xmlns:xlink="http://www.w3.org/1999/xlink"
				xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsd="http://www.w3.org/2001/XMLSchema"
				xmlns:lcl="http://www.efatura.gov.tr/local"
				xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
				exclude-result-prefixes="cac cbc ccts clm54217 clm5639 clm66411 clmIANAMIMEMediaType fn link n1 qdt udt xbrldi xbrli xdt xlink xs xsd xsi lcl">
	<xsl:character-map name="a">
		<xsl:output-character character="&#128;" string=""/>
		<xsl:output-character character="&#129;" string=""/>
		<xsl:output-character character="&#130;" string=""/>
		<xsl:output-character character="&#131;" string=""/>
		<xsl:output-character character="&#132;" string=""/>
		<xsl:output-character character="&#133;" string=""/>
		<xsl:output-character character="&#134;" string=""/>
		<xsl:output-character character="&#135;" string=""/>
		<xsl:output-character character="&#136;" string=""/>
		<xsl:output-character character="&#137;" string=""/>
		<xsl:output-character character="&#138;" string=""/>
		<xsl:output-character character="&#139;" string=""/>
		<xsl:output-character character="&#140;" string=""/>
		<xsl:output-character character="&#141;" string=""/>
		<xsl:output-character character="&#142;" string=""/>
		<xsl:output-character character="&#143;" string=""/>
		<xsl:output-character character="&#144;" string=""/>
		<xsl:output-character character="&#145;" string=""/>
		<xsl:output-character character="&#146;" string=""/>
		<xsl:output-character character="&#147;" string=""/>
		<xsl:output-character character="&#148;" string=""/>
		<xsl:output-character character="&#149;" string=""/>
		<xsl:output-character character="&#150;" string=""/>
		<xsl:output-character character="&#151;" string=""/>
		<xsl:output-character character="&#152;" string=""/>
		<xsl:output-character character="&#153;" string=""/>
		<xsl:output-character character="&#154;" string=""/>
		<xsl:output-character character="&#155;" string=""/>
		<xsl:output-character character="&#156;" string=""/>
		<xsl:output-character character="&#157;" string=""/>
		<xsl:output-character character="&#158;" string=""/>
		<xsl:output-character character="&#159;" string=""/>
	</xsl:character-map>
	<xsl:decimal-format name="european" decimal-separator="," grouping-separator="." NaN=""/>
	<xsl:output version="4.0" method="html" indent="no" encoding="UTF-8"
				doctype-public="-//W3C//DTD HTML 4.01 Transitional//EN"
				doctype-system="http://www.w3.org/TR/html4/loose.dtd" use-character-maps="a"/>
	<xsl:param name="SV_OutputFormat" select="'HTML'"/>
	<xsl:variable name="XML" select="/"/>
	<xsl:variable name="vareczanehizmetbedeli">
		<xsl:for-each select="//n1:Invoice/cbc:Note">
			<xsl:choose>
				<xsl:when test="substring(.,0,9) = 'SGK_EHB:'">
					<xsl:variable name="vareczanehizmetbedeliControl" select="normalize-space(substring-after(substring(.,8),':'))"/>
					<xsl:choose>
						<xsl:when test="$vareczanehizmetbedeliControl != 'null' and $vareczanehizmetbedeliControl">
							<xsl:value-of select="$vareczanehizmetbedeliControl"/>
						</xsl:when>
						<xsl:otherwise>
							<xsl:value-of select="0"/>
						</xsl:otherwise>
					</xsl:choose>
				</xsl:when>
			</xsl:choose>
		</xsl:for-each>
	</xsl:variable>
	<xsl:variable name="vareczanehizmetbedeli20">
		<xsl:for-each select="//n1:Invoice/cbc:Note">
			<xsl:choose>
				<xsl:when test="substring(.,0,11) = 'SGK_EHB20:'">
					<xsl:variable name="vareczanehizmetbedeli20Control" select="normalize-space(substring-after(substring(.,8),':'))"/>
					<xsl:choose>
						<xsl:when test="$vareczanehizmetbedeli20Control != 'null' and $vareczanehizmetbedeli20Control">
							<xsl:value-of select="$vareczanehizmetbedeli20Control"/>
						</xsl:when>
						<xsl:otherwise>
							<xsl:value-of select="0"/>
						</xsl:otherwise>
					</xsl:choose>
				</xsl:when>
			</xsl:choose>
		</xsl:for-each>
	</xsl:variable>
	<xsl:variable name="vartutar">
		<xsl:for-each select="//n1:Invoice/cbc:Note">
			<xsl:choose>
				<xsl:when test="substring(.,0,9) = 'SGK_BRT:'">
					<xsl:value-of select="normalize-space(substring-after(substring(.,8),':'))" />
				</xsl:when>
			</xsl:choose>
		</xsl:for-each>
	</xsl:variable>
	<xsl:variable name="variskonto">
		<xsl:for-each select="//n1:Invoice/cbc:Note">
			<xsl:choose>
				<xsl:when test="substring(.,0,9) = 'SGK_ISK:'">
					<xsl:value-of select="normalize-space(substring-after(substring(.,8),':'))" />
				</xsl:when>
			</xsl:choose>
		</xsl:for-each>
	</xsl:variable>
	<xsl:variable name="varkatilimpayi">
		<xsl:for-each select="//n1:Invoice/cbc:Note">
			<xsl:choose>
				<xsl:when test="substring(.,0,9) = 'SGK_HKP:'">
					<xsl:value-of select="normalize-space(substring-after(substring(.,8),':'))" />
				</xsl:when>
			</xsl:choose>
		</xsl:for-each>
	</xsl:variable>
	<xsl:variable name="varisitmekatilimpayi">
		<xsl:for-each select="//n1:Invoice/cbc:Note">
			<xsl:choose>
				<xsl:when test="substring(.,0,9) = 'SGK_IKP:'">
					<xsl:value-of select="normalize-space(substring-after(substring(.,8),':'))" />
				</xsl:when>
			</xsl:choose>
		</xsl:for-each>
	</xsl:variable>
	<xsl:variable name="varilacfarki">
		<xsl:for-each select="//n1:Invoice/cbc:Note">
			<xsl:choose>
				<xsl:when test="substring(.,0,9) = 'SGK_ILF:'">
					<xsl:value-of select="normalize-space(substring-after(substring(.,8),':'))" />
				</xsl:when>
			</xsl:choose>
		</xsl:for-each>
	</xsl:variable>
	<xsl:variable name="varsiparissorumlusu">
		<xsl:for-each select="//n1:Invoice/cbc:Note">
			<xsl:choose>
				<xsl:when test="substring(.,0,4) = 'SS:'">
					<xsl:value-of select="normalize-space(substring-after(substring(.,3),':'))" />
				</xsl:when>
			</xsl:choose>
		</xsl:for-each>
	</xsl:variable>
	<xsl:variable name="varkdv8">
		<xsl:for-each select="//n1:Invoice/cbc:Note">
			<xsl:choose>
				<xsl:when test="substring(.,0,9) = 'SGK_K08:'">
					<xsl:variable name="varkdv8Control" select="normalize-space(substring-after(substring(.,8),':'))" />
					<xsl:choose>
						<xsl:when test="$varkdv8Control != 'null' and $varkdv8Control">
							<xsl:value-of select="$varkdv8Control" />
						</xsl:when>
						<xsl:otherwise>
							<xsl:value-of select="0"/>
						</xsl:otherwise>
					</xsl:choose>
				</xsl:when>
			</xsl:choose>
		</xsl:for-each>
	</xsl:variable>
	<xsl:variable name="varkdv10">
		<xsl:for-each select="//n1:Invoice/cbc:Note">
			<xsl:choose>
				<xsl:when test="substring(.,0,9) = 'SGK_K10:'">
					<xsl:variable name="varkdv10Control" select="normalize-space(substring-after(substring(.,8),':'))" />
					<xsl:choose>
						<xsl:when test="$varkdv10Control != 'null' and $varkdv10Control != 'undefined'">
							<xsl:value-of select="$varkdv10Control" />
						</xsl:when>
						<xsl:otherwise>
							<xsl:value-of select="0"/>
						</xsl:otherwise>
					</xsl:choose>
				</xsl:when>
			</xsl:choose>
		</xsl:for-each>
	</xsl:variable>
	<xsl:variable name="varkdv18">
		<xsl:for-each select="//n1:Invoice/cbc:Note">
			<xsl:choose>
				<xsl:when test="substring(.,0,9) = 'SGK_K18:'">
					<xsl:variable name="varkdv18Control" select="normalize-space(substring-after(substring(.,8),':'))" />
					<xsl:choose>
						<xsl:when test="$varkdv18Control != 'null' and $varkdv18Control != 'undefined'">
							<xsl:value-of select="$varkdv18Control" />
						</xsl:when>
						<xsl:otherwise>
							<xsl:value-of select="0"/>
						</xsl:otherwise>
					</xsl:choose>
				</xsl:when>
			</xsl:choose>
		</xsl:for-each>
	</xsl:variable>
	<xsl:variable name="varkdv20">
		<xsl:for-each select="//n1:Invoice/cbc:Note">
			<xsl:choose>
				<xsl:when test="substring(.,0,9) = 'SGK_K20:'">
					<xsl:variable name="varkdv20Control" select="normalize-space(substring-after(substring(.,8),':'))" />
					<xsl:choose>
						<xsl:when test="$varkdv20Control != 'null' and $varkdv20Control != 'undefined'">
							<xsl:value-of select="$varkdv20Control" />
						</xsl:when>
						<xsl:otherwise>
							<xsl:value-of select="0"/>
						</xsl:otherwise>
					</xsl:choose>
				</xsl:when>
			</xsl:choose>
		</xsl:for-each>
	</xsl:variable>
	<xsl:variable name="vareczanekdv18">
		<xsl:for-each select="//n1:Invoice/cbc:Note">
			<xsl:choose>
				<xsl:when test="substring(.,0,9) = 'SGK_EHK:'">
					<xsl:variable name="vareczanekdv18Control" select="normalize-space(substring-after(substring(.,8),':'))" />
					<xsl:choose>
						<xsl:when test="$vareczanekdv18Control != 'null' and $vareczanekdv18Control != 'undefined'">
							<xsl:value-of select="$vareczanekdv18Control" />
						</xsl:when>
						<xsl:otherwise>
							<xsl:value-of select="0"/>
						</xsl:otherwise>
					</xsl:choose>
				</xsl:when>
			</xsl:choose>
		</xsl:for-each>
	</xsl:variable>
	<xsl:variable name="vareczanekdv20">
		<xsl:for-each select="//n1:Invoice/cbc:Note">
			<xsl:choose>
				<xsl:when test="substring(.,0,11) = 'SGK_EHK20:'">
					<xsl:variable name="vareczanekdv20Control" select="normalize-space(substring-after(substring(.,8),':'))" />
					<xsl:choose>
						<xsl:when test="$vareczanekdv20Control != 'null' and $vareczanekdv20Control != 'undefined'">
							<xsl:value-of select="$vareczanekdv20Control" />
						</xsl:when>
						<xsl:otherwise>
							<xsl:value-of select="0"/>
						</xsl:otherwise>
					</xsl:choose>
				</xsl:when>
			</xsl:choose>
		</xsl:for-each>
	</xsl:variable>
	<xsl:variable name="varpsf">
		<xsl:for-each select="//n1:Invoice/cbc:Note">
			<xsl:choose>
				<xsl:when test="substring(.,0,9) = 'SGK_PSF:'">
					<xsl:value-of select="normalize-space(substring-after(substring(.,8),':'))" />
				</xsl:when>
			</xsl:choose>
		</xsl:for-each>
	</xsl:variable>
	<xsl:variable name="varreceteadedi">
		<xsl:for-each select="//n1:Invoice/cbc:Note">
			<xsl:choose>
				<xsl:when test="substring(.,0,9) = 'SGK_RCA:'">
					<xsl:value-of select="substring-after(substring(.,8),':')" />
				</xsl:when>
			</xsl:choose>
		</xsl:for-each>
	</xsl:variable>
	<xsl:variable name="vareldenilackatilimpayi">
		<xsl:for-each select="//n1:Invoice/cbc:Note">
			<xsl:choose>
				<xsl:when test="substring(.,0,9) = 'SGK_EIP:'">
					<xsl:value-of select="normalize-space(substring-after(substring(.,8),':'))" />
				</xsl:when>
			</xsl:choose>
		</xsl:for-each>
	</xsl:variable>
	<xsl:variable name="varmaasdanilackatilimpayi">
		<xsl:for-each select="//n1:Invoice/cbc:Note">
			<xsl:choose>
				<xsl:when test="substring(.,0,9) = 'SGK_MIP:'">
					<xsl:value-of select="normalize-space(substring-after(substring(.,8),':'))" />
				</xsl:when>
			</xsl:choose>
		</xsl:for-each>
	</xsl:variable>
	<xsl:variable name="vareldenmuayenekatilimpayi">
		<xsl:for-each select="//n1:Invoice/cbc:Note">
			<xsl:choose>
				<xsl:when test="substring(.,0,9) = 'SGK_EMP:'">
					<xsl:value-of select="normalize-space(substring-after(substring(.,8),':'))" />
				</xsl:when>
			</xsl:choose>
		</xsl:for-each>
	</xsl:variable>
	<xsl:variable name="varmaasmuayenekatilimpayi">
		<xsl:for-each select="//n1:Invoice/cbc:Note">
			<xsl:choose>
				<xsl:when test="substring(.,0,9) = 'SGK_MMP:'">
					<xsl:value-of select="normalize-space(substring-after(substring(.,8),':'))" />
				</xsl:when>
			</xsl:choose>
		</xsl:for-each>
	</xsl:variable>
	<xsl:variable name="vareldenrecetekatilimpayi">
		<xsl:for-each select="//n1:Invoice/cbc:Note">
			<xsl:choose>
				<xsl:when test="substring(.,0,9) = 'SGK_ERP:'">
					<xsl:value-of select="normalize-space(substring-after(substring(.,8),':'))" />
				</xsl:when>
			</xsl:choose>
		</xsl:for-each>
	</xsl:variable>
	<xsl:variable name="varmaastanrecetekatilimpayi">
		<xsl:for-each select="//n1:Invoice/cbc:Note">
			<xsl:choose>
				<xsl:when test="substring(.,0,9) = 'SGK_MRP:'">
					<xsl:value-of select="normalize-space(substring-after(substring(.,8),':'))" />
				</xsl:when>
			</xsl:choose>
		</xsl:for-each>
	</xsl:variable>
	<xsl:variable name="varfaturatipi">
		<xsl:for-each select="//n1:Invoice/cbc:Note">
			<xsl:choose>
				<xsl:when test="substring(.,0,12) = 'FATURATIPI:'">
					<xsl:value-of select="normalize-space(substring-after(substring(.,10),':'))" />
				</xsl:when>
			</xsl:choose>
		</xsl:for-each>
	</xsl:variable>
	<xsl:variable name="varoptik">
		<xsl:for-each select="//n1:Invoice/cbc:Note">
			<xsl:choose>
				<xsl:when test="substring(.,0,9) = 'SGK_TYP:'">
					<xsl:value-of select="normalize-space(substring-after(substring(.,7),':'))" />
				</xsl:when>
			</xsl:choose>
		</xsl:for-each>
	</xsl:variable>
	<xsl:variable name="varfaturatype">
	<!--		Cetas ise kullanılacak-->
		<!--TEBEOS Cezaevi faturası için sgk şeklinde bir tasarım istermiştir ona göre düzenleme yapılmıştır.
		Resources altına oluşturdukları xml atılacaktır. Değişiklik yaparken o xmle de görede kontrol sağlanmalıdır.-->
		<xsl:for-each select="//n1:Invoice/cbc:Note">
			<xsl:choose>
				<xsl:when test="substring(.,0,13) = 'FATURA_TYPE:'">
					<xsl:value-of select="normalize-space(substring-after(substring(.,11),':'))" />
				</xsl:when>
			</xsl:choose>
		</xsl:for-each>
	</xsl:variable>
	<xsl:variable name="varExportInsurance" select="count(//cac:Shipment[cbc:InsuranceValueAmount])"/>
	<xsl:variable name="varExportCarriage" select="count(//cac:Shipment[cbc:DeclaredForCarriageValueAmount])"/>
	<xsl:variable name="varEtiketFiyati">
		<xsl:for-each select="//n1:Invoice/cac:InvoiceLine">
			<xsl:for-each select="cbc:Note">
				<xsl:choose>
					<xsl:when test="substring(.,0,5) = 'ETF:' or substring(.,0,5) = 'ESF:'">
						<xsl:value-of select="1" />
					</xsl:when>
				</xsl:choose>
			</xsl:for-each>
		</xsl:for-each>
	</xsl:variable>
	<xsl:variable name="varEczaciKar">
		<xsl:for-each select="//n1:Invoice/cac:InvoiceLine">
			<xsl:for-each select="cbc:Note">
				<xsl:choose>
					<xsl:when test="substring(.,0,5) = 'ECK:' or substring(.,0,5) = 'EKO:'">
						<xsl:value-of select="1" />
					</xsl:when>
				</xsl:choose>
			</xsl:for-each>
		</xsl:for-each>
	</xsl:variable>
	<xsl:variable name="varKurumIskonto">
		<xsl:for-each select="//n1:Invoice/cac:InvoiceLine">
			<xsl:for-each select="cbc:Note">
				<xsl:choose>
					<xsl:when test="substring(.,0,5) = 'KRI:'">
						<xsl:value-of select="1" />
					</xsl:when>
				</xsl:choose>
			</xsl:for-each>
		</xsl:for-each>
	</xsl:variable>
	<xsl:variable name="varDepocuFiyati">
		<xsl:for-each select="//n1:Invoice/cac:InvoiceLine">
			<xsl:for-each select="cbc:Note">
				<xsl:choose>
					<xsl:when test="substring(.,0,5) = 'DSF:'">
						<xsl:value-of select="1" />
					</xsl:when>
				</xsl:choose>
			</xsl:for-each>
		</xsl:for-each>
	</xsl:variable>
	<xsl:variable name="varVade">
		<xsl:for-each select="//n1:Invoice/cac:InvoiceLine">
			<xsl:for-each select="cbc:Note">
				<xsl:choose>
					<xsl:when test="substring(.,0,5) = 'VAD:'">
						<xsl:value-of select="1" />
					</xsl:when>
				</xsl:choose>
			</xsl:for-each>
		</xsl:for-each>
	</xsl:variable>
	<xsl:variable name="varBranchName">
		<xsl:for-each select="//n1:Invoice/cac:AdditionalDocumentReference/cbc:DocumentTypeCode[text()='SUBE_UNVAN']">
			<xsl:choose>
				<xsl:when	test="../cbc:DocumentTypeCode='SUBE_UNVAN'">
					<xsl:value-of select="1" />
				</xsl:when>
			</xsl:choose>
		</xsl:for-each>
	</xsl:variable>

	<xsl:variable name="varSenaryoName">
		<xsl:for-each select="//n1:Invoice/cbc:ProfileID">
			<xsl:choose>
				<xsl:when test="substring(.,0,5) = 'KAMU'">
					<xsl:value-of select="1" />
				</xsl:when>
			</xsl:choose>
		</xsl:for-each>
	</xsl:variable>
	<xsl:variable name="varVknComp">
		<xsl:if test="(//n1:Invoice/cac:AccountingCustomerParty/cac:Party/cac:PartyIdentification/cbc:ID[@schemeID='VKN'])=(//n1:Invoice/cac:BuyerCustomerParty/cac:Party/cac:PartyIdentification/cbc:ID[@schemeID='VKN'])">
			<xsl:value-of select="1" />
		</xsl:if>
	</xsl:variable>

	<xsl:variable name="varItemCode" select="count(//cac:SellersItemIdentification[cbc:ID !=''])"/>
	<xsl:variable name="varAllowanceRate" select="count(//n1:Invoice/cac:InvoiceLine/cac:AllowanceCharge[cbc:MultiplierFactorNumeric !=''])"/>
	<xsl:variable name="varAllowanceAmount" select="count(//n1:Invoice/cac:InvoiceLine/cac:AllowanceCharge[cbc:Amount !=''])"/>
	<xsl:variable name="varAllowanceReason" select="count(//n1:Invoice/cac:InvoiceLine/cac:AllowanceCharge[cbc:AllowanceChargeReason !=''])"/>
	<xsl:variable name="varLineExplanation" select="count(//n1:Invoice/cac:InvoiceLine[cbc:Note !=''])"/>

	<xsl:template match="/">
		<html>
			<head>
				<script type="text/javascript">
					<![CDATA[var QRCode;!function(){function a(a){this.mode=c.MODE_8BIT_BYTE,this.data=a,this.parsedData=[];for(var b=[],d=0,e=this.data.length;e>d;d++){var f=this.data.charCodeAt(d);f>65536?(b[0]=240|(1835008&f)>>>18,b[1]=128|(258048&f)>>>12,b[2]=128|(4032&f)>>>6,b[3]=128|63&f):f>2048?(b[0]=224|(61440&f)>>>12,b[1]=128|(4032&f)>>>6,b[2]=128|63&f):f>128?(b[0]=192|(1984&f)>>>6,b[1]=128|63&f):b[0]=f,this.parsedData=this.parsedData.concat(b)}this.parsedData.length!=this.data.length&&(this.parsedData.unshift(191),this.parsedData.unshift(187),this.parsedData.unshift(239))}function b(a,b){this.typeNumber=a,this.errorCorrectLevel=b,this.modules=null,this.moduleCount=0,this.dataCache=null,this.dataList=[]}function i(a,b){if(void 0==a.length)throw new Error(a.length+"/"+b);for(var c=0;c<a.length&&0==a[c];)c++;this.num=new Array(a.length-c+b);for(var d=0;d<a.length-c;d++)this.num[d]=a[d+c]}function j(a,b){this.totalCount=a,this.dataCount=b}function k(){this.buffer=[],this.length=0}function m(){return"undefined"!=typeof CanvasRenderingContext2D}function n(){var a=!1,b=navigator.userAgent;return/android/i.test(b)&&(a=!0,aMat=b.toString().match(/android ([0-9]\.[0-9])/i),aMat&&aMat[1]&&(a=parseFloat(aMat[1]))),a}function r(a,b){for(var c=1,e=s(a),f=0,g=l.length;g>=f;f++){var h=0;switch(b){case d.L:h=l[f][0];break;case d.M:h=l[f][1];break;case d.Q:h=l[f][2];break;case d.H:h=l[f][3]}if(h>=e)break;c++}if(c>l.length)throw new Error("Too long data");return c}function s(a){var b=encodeURI(a).toString().replace(/\%[0-9a-fA-F]{2}/g,"a");return b.length+(b.length!=a?3:0)}a.prototype={getLength:function(){return this.parsedData.length},write:function(a){for(var b=0,c=this.parsedData.length;c>b;b++)a.put(this.parsedData[b],8)}},b.prototype={addData:function(b){var c=new a(b);this.dataList.push(c),this.dataCache=null},isDark:function(a,b){if(0>a||this.moduleCount<=a||0>b||this.moduleCount<=b)throw new Error(a+","+b);return this.modules[a][b]},getModuleCount:function(){return this.moduleCount},make:function(){this.makeImpl(!1,this.getBestMaskPattern())},makeImpl:function(a,c){this.moduleCount=4*this.typeNumber+17,this.modules=new Array(this.moduleCount);for(var d=0;d<this.moduleCount;d++){this.modules[d]=new Array(this.moduleCount);for(var e=0;e<this.moduleCount;e++)this.modules[d][e]=null}this.setupPositionProbePattern(0,0),this.setupPositionProbePattern(this.moduleCount-7,0),this.setupPositionProbePattern(0,this.moduleCount-7),this.setupPositionAdjustPattern(),this.setupTimingPattern(),this.setupTypeInfo(a,c),this.typeNumber>=7&&this.setupTypeNumber(a),null==this.dataCache&&(this.dataCache=b.createData(this.typeNumber,this.errorCorrectLevel,this.dataList)),this.mapData(this.dataCache,c)},setupPositionProbePattern:function(a,b){for(var c=-1;7>=c;c++)if(!(-1>=a+c||this.moduleCount<=a+c))for(var d=-1;7>=d;d++)-1>=b+d||this.moduleCount<=b+d||(this.modules[a+c][b+d]=c>=0&&6>=c&&(0==d||6==d)||d>=0&&6>=d&&(0==c||6==c)||c>=2&&4>=c&&d>=2&&4>=d?!0:!1)},getBestMaskPattern:function(){for(var a=0,b=0,c=0;8>c;c++){this.makeImpl(!0,c);var d=f.getLostPoint(this);(0==c||a>d)&&(a=d,b=c)}return b},createMovieClip:function(a,b,c){var d=a.createEmptyMovieClip(b,c),e=1;this.make();for(var f=0;f<this.modules.length;f++)for(var g=f*e,h=0;h<this.modules[f].length;h++){var i=h*e,j=this.modules[f][h];j&&(d.beginFill(0,100),d.moveTo(i,g),d.lineTo(i+e,g),d.lineTo(i+e,g+e),d.lineTo(i,g+e),d.endFill())}return d},setupTimingPattern:function(){for(var a=8;a<this.moduleCount-8;a++)null==this.modules[a][6]&&(this.modules[a][6]=0==a%2);for(var b=8;b<this.moduleCount-8;b++)null==this.modules[6][b]&&(this.modules[6][b]=0==b%2)},setupPositionAdjustPattern:function(){for(var a=f.getPatternPosition(this.typeNumber),b=0;b<a.length;b++)for(var c=0;c<a.length;c++){var d=a[b],e=a[c];if(null==this.modules[d][e])for(var g=-2;2>=g;g++)for(var h=-2;2>=h;h++)this.modules[d+g][e+h]=-2==g||2==g||-2==h||2==h||0==g&&0==h?!0:!1}},setupTypeNumber:function(a){for(var b=f.getBCHTypeNumber(this.typeNumber),c=0;18>c;c++){var d=!a&&1==(1&b>>c);this.modules[Math.floor(c/3)][c%3+this.moduleCount-8-3]=d}for(var c=0;18>c;c++){var d=!a&&1==(1&b>>c);this.modules[c%3+this.moduleCount-8-3][Math.floor(c/3)]=d}},setupTypeInfo:function(a,b){for(var c=this.errorCorrectLevel<<3|b,d=f.getBCHTypeInfo(c),e=0;15>e;e++){var g=!a&&1==(1&d>>e);6>e?this.modules[e][8]=g:8>e?this.modules[e+1][8]=g:this.modules[this.moduleCount-15+e][8]=g}for(var e=0;15>e;e++){var g=!a&&1==(1&d>>e);8>e?this.modules[8][this.moduleCount-e-1]=g:9>e?this.modules[8][15-e-1+1]=g:this.modules[8][15-e-1]=g}this.modules[this.moduleCount-8][8]=!a},mapData:function(a,b){for(var c=-1,d=this.moduleCount-1,e=7,g=0,h=this.moduleCount-1;h>0;h-=2)for(6==h&&h--;;){for(var i=0;2>i;i++)if(null==this.modules[d][h-i]){var j=!1;g<a.length&&(j=1==(1&a[g]>>>e));var k=f.getMask(b,d,h-i);k&&(j=!j),this.modules[d][h-i]=j,e--,-1==e&&(g++,e=7)}if(d+=c,0>d||this.moduleCount<=d){d-=c,c=-c;break}}}},b.PAD0=236,b.PAD1=17,b.createData=function(a,c,d){for(var e=j.getRSBlocks(a,c),g=new k,h=0;h<d.length;h++){var i=d[h];g.put(i.mode,4),g.put(i.getLength(),f.getLengthInBits(i.mode,a)),i.write(g)}for(var l=0,h=0;h<e.length;h++)l+=e[h].dataCount;if(g.getLengthInBits()>8*l)throw new Error("code length overflow. ("+g.getLengthInBits()+">"+8*l+")");for(g.getLengthInBits()+4<=8*l&&g.put(0,4);0!=g.getLengthInBits()%8;)g.putBit(!1);for(;;){if(g.getLengthInBits()>=8*l)break;if(g.put(b.PAD0,8),g.getLengthInBits()>=8*l)break;g.put(b.PAD1,8)}return b.createBytes(g,e)},b.createBytes=function(a,b){for(var c=0,d=0,e=0,g=new Array(b.length),h=new Array(b.length),j=0;j<b.length;j++){var k=b[j].dataCount,l=b[j].totalCount-k;d=Math.max(d,k),e=Math.max(e,l),g[j]=new Array(k);for(var m=0;m<g[j].length;m++)g[j][m]=255&a.buffer[m+c];c+=k;var n=f.getErrorCorrectPolynomial(l),o=new i(g[j],n.getLength()-1),p=o.mod(n);h[j]=new Array(n.getLength()-1);for(var m=0;m<h[j].length;m++){var q=m+p.getLength()-h[j].length;h[j][m]=q>=0?p.get(q):0}}for(var r=0,m=0;m<b.length;m++)r+=b[m].totalCount;for(var s=new Array(r),t=0,m=0;d>m;m++)for(var j=0;j<b.length;j++)m<g[j].length&&(s[t++]=g[j][m]);for(var m=0;e>m;m++)for(var j=0;j<b.length;j++)m<h[j].length&&(s[t++]=h[j][m]);return s};for(var c={MODE_NUMBER:1,MODE_ALPHA_NUM:2,MODE_8BIT_BYTE:4,MODE_KANJI:8},d={L:1,M:0,Q:3,H:2},e={PATTERN000:0,PATTERN001:1,PATTERN010:2,PATTERN011:3,PATTERN100:4,PATTERN101:5,PATTERN110:6,PATTERN111:7},f={PATTERN_POSITION_TABLE:[[],[6,18],[6,22],[6,26],[6,30],[6,34],[6,22,38],[6,24,42],[6,26,46],[6,28,50],[6,30,54],[6,32,58],[6,34,62],[6,26,46,66],[6,26,48,70],[6,26,50,74],[6,30,54,78],[6,30,56,82],[6,30,58,86],[6,34,62,90],[6,28,50,72,94],[6,26,50,74,98],[6,30,54,78,102],[6,28,54,80,106],[6,32,58,84,110],[6,30,58,86,114],[6,34,62,90,118],[6,26,50,74,98,122],[6,30,54,78,102,126],[6,26,52,78,104,130],[6,30,56,82,108,134],[6,34,60,86,112,138],[6,30,58,86,114,142],[6,34,62,90,118,146],[6,30,54,78,102,126,150],[6,24,50,76,102,128,154],[6,28,54,80,106,132,158],[6,32,58,84,110,136,162],[6,26,54,82,110,138,166],[6,30,58,86,114,142,170]],G15:1335,G18:7973,G15_MASK:21522,getBCHTypeInfo:function(a){for(var b=a<<10;f.getBCHDigit(b)-f.getBCHDigit(f.G15)>=0;)b^=f.G15<<f.getBCHDigit(b)-f.getBCHDigit(f.G15);return(a<<10|b)^f.G15_MASK},getBCHTypeNumber:function(a){for(var b=a<<12;f.getBCHDigit(b)-f.getBCHDigit(f.G18)>=0;)b^=f.G18<<f.getBCHDigit(b)-f.getBCHDigit(f.G18);return a<<12|b},getBCHDigit:function(a){for(var b=0;0!=a;)b++,a>>>=1;return b},getPatternPosition:function(a){return f.PATTERN_POSITION_TABLE[a-1]},getMask:function(a,b,c){switch(a){case e.PATTERN000:return 0==(b+c)%2;case e.PATTERN001:return 0==b%2;case e.PATTERN010:return 0==c%3;case e.PATTERN011:return 0==(b+c)%3;case e.PATTERN100:return 0==(Math.floor(b/2)+Math.floor(c/3))%2;case e.PATTERN101:return 0==b*c%2+b*c%3;case e.PATTERN110:return 0==(b*c%2+b*c%3)%2;case e.PATTERN111:return 0==(b*c%3+(b+c)%2)%2;default:throw new Error("bad maskPattern:"+a)}},getErrorCorrectPolynomial:function(a){for(var b=new i([1],0),c=0;a>c;c++)b=b.multiply(new i([1,g.gexp(c)],0));return b},getLengthInBits:function(a,b){if(b>=1&&10>b)switch(a){case c.MODE_NUMBER:return 10;case c.MODE_ALPHA_NUM:return 9;case c.MODE_8BIT_BYTE:return 8;case c.MODE_KANJI:return 8;default:throw new Error("mode:"+a)}else if(27>b)switch(a){case c.MODE_NUMBER:return 12;case c.MODE_ALPHA_NUM:return 11;case c.MODE_8BIT_BYTE:return 16;case c.MODE_KANJI:return 10;default:throw new Error("mode:"+a)}else{if(!(41>b))throw new Error("type:"+b);switch(a){case c.MODE_NUMBER:return 14;case c.MODE_ALPHA_NUM:return 13;case c.MODE_8BIT_BYTE:return 16;case c.MODE_KANJI:return 12;default:throw new Error("mode:"+a)}}},getLostPoint:function(a){for(var b=a.getModuleCount(),c=0,d=0;b>d;d++)for(var e=0;b>e;e++){for(var f=0,g=a.isDark(d,e),h=-1;1>=h;h++)if(!(0>d+h||d+h>=b))for(var i=-1;1>=i;i++)0>e+i||e+i>=b||(0!=h||0!=i)&&g==a.isDark(d+h,e+i)&&f++;f>5&&(c+=3+f-5)}for(var d=0;b-1>d;d++)for(var e=0;b-1>e;e++){var j=0;a.isDark(d,e)&&j++,a.isDark(d+1,e)&&j++,a.isDark(d,e+1)&&j++,a.isDark(d+1,e+1)&&j++,(0==j||4==j)&&(c+=3)}for(var d=0;b>d;d++)for(var e=0;b-6>e;e++)a.isDark(d,e)&&!a.isDark(d,e+1)&&a.isDark(d,e+2)&&a.isDark(d,e+3)&&a.isDark(d,e+4)&&!a.isDark(d,e+5)&&a.isDark(d,e+6)&&(c+=40);for(var e=0;b>e;e++)for(var d=0;b-6>d;d++)a.isDark(d,e)&&!a.isDark(d+1,e)&&a.isDark(d+2,e)&&a.isDark(d+3,e)&&a.isDark(d+4,e)&&!a.isDark(d+5,e)&&a.isDark(d+6,e)&&(c+=40);for(var k=0,e=0;b>e;e++)for(var d=0;b>d;d++)a.isDark(d,e)&&k++;var l=Math.abs(100*k/b/b-50)/5;return c+=10*l}},g={glog:function(a){if(1>a)throw new Error("glog("+a+")");return g.LOG_TABLE[a]},gexp:function(a){for(;0>a;)a+=255;for(;a>=256;)a-=255;return g.EXP_TABLE[a]},EXP_TABLE:new Array(256),LOG_TABLE:new Array(256)},h=0;8>h;h++)g.EXP_TABLE[h]=1<<h;for(var h=8;256>h;h++)g.EXP_TABLE[h]=g.EXP_TABLE[h-4]^g.EXP_TABLE[h-5]^g.EXP_TABLE[h-6]^g.EXP_TABLE[h-8];for(var h=0;255>h;h++)g.LOG_TABLE[g.EXP_TABLE[h]]=h;i.prototype={get:function(a){return this.num[a]},getLength:function(){return this.num.length},multiply:function(a){for(var b=new Array(this.getLength()+a.getLength()-1),c=0;c<this.getLength();c++)for(var d=0;d<a.getLength();d++)b[c+d]^=g.gexp(g.glog(this.get(c))+g.glog(a.get(d)));return new i(b,0)},mod:function(a){if(this.getLength()-a.getLength()<0)return this;for(var b=g.glog(this.get(0))-g.glog(a.get(0)),c=new Array(this.getLength()),d=0;d<this.getLength();d++)c[d]=this.get(d);for(var d=0;d<a.getLength();d++)c[d]^=g.gexp(g.glog(a.get(d))+b);return new i(c,0).mod(a)}},j.RS_BLOCK_TABLE=[[1,26,19],[1,26,16],[1,26,13],[1,26,9],[1,44,34],[1,44,28],[1,44,22],[1,44,16],[1,70,55],[1,70,44],[2,35,17],[2,35,13],[1,100,80],[2,50,32],[2,50,24],[4,25,9],[1,134,108],[2,67,43],[2,33,15,2,34,16],[2,33,11,2,34,12],[2,86,68],[4,43,27],[4,43,19],[4,43,15],[2,98,78],[4,49,31],[2,32,14,4,33,15],[4,39,13,1,40,14],[2,121,97],[2,60,38,2,61,39],[4,40,18,2,41,19],[4,40,14,2,41,15],[2,146,116],[3,58,36,2,59,37],[4,36,16,4,37,17],[4,36,12,4,37,13],[2,86,68,2,87,69],[4,69,43,1,70,44],[6,43,19,2,44,20],[6,43,15,2,44,16],[4,101,81],[1,80,50,4,81,51],[4,50,22,4,51,23],[3,36,12,8,37,13],[2,116,92,2,117,93],[6,58,36,2,59,37],[4,46,20,6,47,21],[7,42,14,4,43,15],[4,133,107],[8,59,37,1,60,38],[8,44,20,4,45,21],[12,33,11,4,34,12],[3,145,115,1,146,116],[4,64,40,5,65,41],[11,36,16,5,37,17],[11,36,12,5,37,13],[5,109,87,1,110,88],[5,65,41,5,66,42],[5,54,24,7,55,25],[11,36,12],[5,122,98,1,123,99],[7,73,45,3,74,46],[15,43,19,2,44,20],[3,45,15,13,46,16],[1,135,107,5,136,108],[10,74,46,1,75,47],[1,50,22,15,51,23],[2,42,14,17,43,15],[5,150,120,1,151,121],[9,69,43,4,70,44],[17,50,22,1,51,23],[2,42,14,19,43,15],[3,141,113,4,142,114],[3,70,44,11,71,45],[17,47,21,4,48,22],[9,39,13,16,40,14],[3,135,107,5,136,108],[3,67,41,13,68,42],[15,54,24,5,55,25],[15,43,15,10,44,16],[4,144,116,4,145,117],[17,68,42],[17,50,22,6,51,23],[19,46,16,6,47,17],[2,139,111,7,140,112],[17,74,46],[7,54,24,16,55,25],[34,37,13],[4,151,121,5,152,122],[4,75,47,14,76,48],[11,54,24,14,55,25],[16,45,15,14,46,16],[6,147,117,4,148,118],[6,73,45,14,74,46],[11,54,24,16,55,25],[30,46,16,2,47,17],[8,132,106,4,133,107],[8,75,47,13,76,48],[7,54,24,22,55,25],[22,45,15,13,46,16],[10,142,114,2,143,115],[19,74,46,4,75,47],[28,50,22,6,51,23],[33,46,16,4,47,17],[8,152,122,4,153,123],[22,73,45,3,74,46],[8,53,23,26,54,24],[12,45,15,28,46,16],[3,147,117,10,148,118],[3,73,45,23,74,46],[4,54,24,31,55,25],[11,45,15,31,46,16],[7,146,116,7,147,117],[21,73,45,7,74,46],[1,53,23,37,54,24],[19,45,15,26,46,16],[5,145,115,10,146,116],[19,75,47,10,76,48],[15,54,24,25,55,25],[23,45,15,25,46,16],[13,145,115,3,146,116],[2,74,46,29,75,47],[42,54,24,1,55,25],[23,45,15,28,46,16],[17,145,115],[10,74,46,23,75,47],[10,54,24,35,55,25],[19,45,15,35,46,16],[17,145,115,1,146,116],[14,74,46,21,75,47],[29,54,24,19,55,25],[11,45,15,46,46,16],[13,145,115,6,146,116],[14,74,46,23,75,47],[44,54,24,7,55,25],[59,46,16,1,47,17],[12,151,121,7,152,122],[12,75,47,26,76,48],[39,54,24,14,55,25],[22,45,15,41,46,16],[6,151,121,14,152,122],[6,75,47,34,76,48],[46,54,24,10,55,25],[2,45,15,64,46,16],[17,152,122,4,153,123],[29,74,46,14,75,47],[49,54,24,10,55,25],[24,45,15,46,46,16],[4,152,122,18,153,123],[13,74,46,32,75,47],[48,54,24,14,55,25],[42,45,15,32,46,16],[20,147,117,4,148,118],[40,75,47,7,76,48],[43,54,24,22,55,25],[10,45,15,67,46,16],[19,148,118,6,149,119],[18,75,47,31,76,48],[34,54,24,34,55,25],[20,45,15,61,46,16]],j.getRSBlocks=function(a,b){var c=j.getRsBlockTable(a,b);if(void 0==c)throw new Error("bad rs block @ typeNumber:"+a+"/errorCorrectLevel:"+b);for(var d=c.length/3,e=[],f=0;d>f;f++)for(var g=c[3*f+0],h=c[3*f+1],i=c[3*f+2],k=0;g>k;k++)e.push(new j(h,i));return e},j.getRsBlockTable=function(a,b){switch(b){case d.L:return j.RS_BLOCK_TABLE[4*(a-1)+0];case d.M:return j.RS_BLOCK_TABLE[4*(a-1)+1];case d.Q:return j.RS_BLOCK_TABLE[4*(a-1)+2];case d.H:return j.RS_BLOCK_TABLE[4*(a-1)+3];default:return void 0}},k.prototype={get:function(a){var b=Math.floor(a/8);return 1==(1&this.buffer[b]>>>7-a%8)},put:function(a,b){for(var c=0;b>c;c++)this.putBit(1==(1&a>>>b-c-1))},getLengthInBits:function(){return this.length},putBit:function(a){var b=Math.floor(this.length/8);this.buffer.length<=b&&this.buffer.push(0),a&&(this.buffer[b]|=128>>>this.length%8),this.length++}};var l=[[17,14,11,7],[32,26,20,14],[53,42,32,24],[78,62,46,34],[106,84,60,44],[134,106,74,58],[154,122,86,64],[192,152,108,84],[230,180,130,98],[271,213,151,119],[321,251,177,137],[367,287,203,155],[425,331,241,177],[458,362,258,194],[520,412,292,220],[586,450,322,250],[644,504,364,280],[718,560,394,310],[792,624,442,338],[858,666,482,382],[929,711,509,403],[1003,779,565,439],[1091,857,611,461],[1171,911,661,511],[1273,997,715,535],[1367,1059,751,593],[1465,1125,805,625],[1528,1190,868,658],[1628,1264,908,698],[1732,1370,982,742],[1840,1452,1030,790],[1952,1538,1112,842],[2068,1628,1168,898],[2188,1722,1228,958],[2303,1809,1283,983],[2431,1911,1351,1051],[2563,1989,1423,1093],[2699,2099,1499,1139],[2809,2213,1579,1219],[2953,2331,1663,1273]],o=function(){var a=function(a,b){this._el=a,this._htOption=b};return a.prototype.draw=function(a){function g(a,b){var c=document.createElementNS("http://www.w3.org/2000/svg",a);for(var d in b)b.hasOwnProperty(d)&&c.setAttribute(d,b[d]);return c}var b=this._htOption,c=this._el,d=a.getModuleCount();Math.floor(b.width/d),Math.floor(b.height/d),this.clear();var h=g("svg",{viewBox:"0 0 "+String(d)+" "+String(d),width:"100%",height:"100%",fill:b.colorLight});h.setAttributeNS("http://www.w3.org/2000/xmlns/","xmlns:xlink","http://www.w3.org/1999/xlink"),c.appendChild(h),h.appendChild(g("rect",{fill:b.colorDark,width:"1",height:"1",id:"template"}));for(var i=0;d>i;i++)for(var j=0;d>j;j++)if(a.isDark(i,j)){var k=g("use",{x:String(i),y:String(j)});k.setAttributeNS("http://www.w3.org/1999/xlink","href","#template"),h.appendChild(k)}},a.prototype.clear=function(){for(;this._el.hasChildNodes();)this._el.removeChild(this._el.lastChild)},a}(),p="svg"===document.documentElement.tagName.toLowerCase(),q=p?o:m()?function(){function a(){this._elImage.src=this._elCanvas.toDataURL("image/png"),this._elImage.style.display="block",this._elCanvas.style.display="none"}function d(a,b){var c=this;if(c._fFail=b,c._fSuccess=a,null===c._bSupportDataURI){var d=document.createElement("img"),e=function(){c._bSupportDataURI=!1,c._fFail&&_fFail.call(c)},f=function(){c._bSupportDataURI=!0,c._fSuccess&&c._fSuccess.call(c)};return d.onabort=e,d.onerror=e,d.onload=f,d.src="data:image/gif;base64,iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg==",void 0}c._bSupportDataURI===!0&&c._fSuccess?c._fSuccess.call(c):c._bSupportDataURI===!1&&c._fFail&&c._fFail.call(c)}if(this._android&&this._android<=2.1){var b=1/window.devicePixelRatio,c=CanvasRenderingContext2D.prototype.drawImage;CanvasRenderingContext2D.prototype.drawImage=function(a,d,e,f,g,h,i,j){if("nodeName"in a&&/img/i.test(a.nodeName))for(var l=arguments.length-1;l>=1;l--)arguments[l]=arguments[l]*b;else"undefined"==typeof j&&(arguments[1]*=b,arguments[2]*=b,arguments[3]*=b,arguments[4]*=b);c.apply(this,arguments)}}var e=function(a,b){this._bIsPainted=!1,this._android=n(),this._htOption=b,this._elCanvas=document.createElement("canvas"),this._elCanvas.width=b.width,this._elCanvas.height=b.height,a.appendChild(this._elCanvas),this._el=a,this._oContext=this._elCanvas.getContext("2d"),this._bIsPainted=!1,this._elImage=document.createElement("img"),this._elImage.style.display="none",this._el.appendChild(this._elImage),this._bSupportDataURI=null};return e.prototype.draw=function(a){var b=this._elImage,c=this._oContext,d=this._htOption,e=a.getModuleCount(),f=d.width/e,g=d.height/e,h=Math.round(f),i=Math.round(g);b.style.display="none",this.clear();for(var j=0;e>j;j++)for(var k=0;e>k;k++){var l=a.isDark(j,k),m=k*f,n=j*g;c.strokeStyle=l?d.colorDark:d.colorLight,c.lineWidth=1,c.fillStyle=l?d.colorDark:d.colorLight,c.fillRect(m,n,f,g),c.strokeRect(Math.floor(m)+.5,Math.floor(n)+.5,h,i),c.strokeRect(Math.ceil(m)-.5,Math.ceil(n)-.5,h,i)}this._bIsPainted=!0},e.prototype.makeImage=function(){this._bIsPainted&&d.call(this,a)},e.prototype.isPainted=function(){return this._bIsPainted},e.prototype.clear=function(){this._oContext.clearRect(0,0,this._elCanvas.width,this._elCanvas.height),this._bIsPainted=!1},e.prototype.round=function(a){return a?Math.floor(1e3*a)/1e3:a},e}():function(){var a=function(a,b){this._el=a,this._htOption=b};return a.prototype.draw=function(a){for(var b=this._htOption,c=this._el,d=a.getModuleCount(),e=Math.floor(b.width/d),f=Math.floor(b.height/d),g=['<table style="border:0;border-collapse:collapse;">'],h=0;d>h;h++){g.push("<tr>");for(var i=0;d>i;i++)g.push('<td style="border:0;border-collapse:collapse;padding:0;margin:0;width:'+e+"px;height:"+f+"px;background-color:"+(a.isDark(h,i)?b.colorDark:b.colorLight)+';"></td>');g.push("</tr>")}g.push("</table>"),c.innerHTML=g.join("");var j=c.childNodes[0],k=(b.width-j.offsetWidth)/2,l=(b.height-j.offsetHeight)/2;k>0&&l>0&&(j.style.margin=l+"px "+k+"px")},a.prototype.clear=function(){this._el.innerHTML=""},a}();QRCode=function(a,b){if(this._htOption={width:256,height:256,typeNumber:4,colorDark:"#000000",colorLight:"#ffffff",correctLevel:d.H},"string"==typeof b&&(b={text:b}),b)for(var c in b)this._htOption[c]=b[c];"string"==typeof a&&(a=document.getElementById(a)),this._android=n(),this._el=a,this._oQRCode=null,this._oDrawing=new q(this._el,this._htOption),this._htOption.text&&this.makeCode(this._htOption.text)},QRCode.prototype.makeCode=function(a){this._oQRCode=new b(r(a,this._htOption.correctLevel),this._htOption.correctLevel),this._oQRCode.addData(a),this._oQRCode.make(),this._el.title=a,this._oDrawing.draw(this._oQRCode),this.makeImage()},QRCode.prototype.makeImage=function(){"function"==typeof this._oDrawing.makeImage&&(!this._android||this._android>=3)&&this._oDrawing.makeImage()},QRCode.prototype.clear=function(){this._oDrawing.clear()},QRCode.CorrectLevel=d}();]]>
				</script>
				<style type="text/css">
					body {
					background-color: #FFFFFF;
					font-family: 'Tahoma', "Times New Roman", Times, serif;
					font-size: 11px;
					color: #000000;
					}
					h1, h2 {
					padding-bottom: 3px;
					padding-top: 3px;
					margin-bottom: 5px;
					text-transform: uppercase;
					font-family: Arial, Helvetica, sans-serif;
					}
					h1 {
					font-size: 1.4em;
					text-transform:none;
					}
					h2 {
					font-size: 1em;
					color: brown;
					}
					h3 {
					font-size: 1em;
					color: #000000;
					text-align: justify;
					margin: 0;
					padding: 0;
					}
					h4 {
					font-size: 1.1em;
					font-style: bold;
					font-family: Arial, Helvetica, sans-serif;
					color: #000000;
					margin: 0;
					padding: 0;
					}
					hr {
					height:2px;
					color: #000000;
					background-color: #000000;
					border-bottom: 1px solid #000000;
					}
					p, ul, ol {
					margin-top: 1.5em;
					}
					ul, ol {
					margin-left: 3em;
					}
					blockquote {
					margin-left: 3em;
					margin-right: 3em;
					font-style: italic;
					}
					a {
					text-decoration: none;
					color: #70A300;
					}
					a:hover {
					border: none;
					color: #70A300;
					}
					#customerPartyTable {
					border-width: 0px;
					border-spacing:;
					border-style: inset;
					border-color: gray;
					border-collapse: collapse;
					background-color:
					}
					#customerIDTable {
					border-width: 2px;
					border-spacing:;
					border-style: inset;
					border-color: gray;
					border-collapse: collapse;
					background-color:
					}
					#customerIDTableTd {
					border-width: 2px;
					border-spacing:;
					border-style: inset;
					border-color: gray;
					border-collapse: collapse;
					background-color:
					}
					#lineTable {
					border-width:2px;
					border-spacing:;
					border-style: inset;
					border-color: black;
					border-collapse: collapse;
					background-color:;
					}
					td.lineTableTd {
					border-width: 1px;
					padding: 1px;
					border-style: inset;
					border-color: black;
					background-color: white;
					}
					#lineTableDummyTd {
					border-width: 1px;
					border-color:white;
					padding: 1px;
					border-style: inset;
					border-color: black;
					background-color: white;
					}
					td.lineTableBudgetTd {
					border-width: 2px;
					border-spacing:0px;
					padding: 1px;
					border-style: inset;
					border-color: black;
					background-color: white;
					-moz-border-radius:;
					}
					#notesTable {
					border-width: 2px;
					border-spacing:;
					border-style: inset;
					border-color: black;
					<!-- border-collapse: collapse; -->
					background-color:
					}
					#notesTableTd {
					border-width: 0px;
					border-spacing:;
					border-style: inset;
					border-color: black;
					border-collapse: collapse;
					background-color:
					}
					table {
					border-spacing:0px;
					}
					#budgetContainerTable {
					border-width: 0px;
					border-spacing: 0px;
					border-style: inset;
					border-color: black;
					border-collapse: collapse;
					background-color:;
					}
					td {
					border-color:gray;
					}
					#invoice-info-td {
					border-style: solid;
					border-width: 1px;
					width: 50%;
					}
					#invoice-line-td {
					border-style: solid;
					border-width: 1px;
					}
				</style>
				<title>e-Belge</title>
			</head>

			<body style="width:800px;">
				<xsl:for-each select="$XML">



					<!-- GONDERICI - EARSIV LOGO - FIRMA LOGO TABLOSU -->
					<table style="width: 100%;">
						<tbody>
							<tr>
								<td style="width: 40%;">
									<hr/>


									<!-- GONDERICI TABLOSU -->
									<table style="width: 100%;">
										<tbody>
											<tr align="left">
												<td align="left">
													<xsl:if test="count(//n1:Invoice/cac:AdditionalDocumentReference/cbc:DocumentTypeCode[text()='SUBE_UNVAN']) &gt;= 1">
														<xsl:for-each select="//n1:Invoice/cac:AdditionalDocumentReference/cbc:DocumentTypeCode[text()='SUBE_UNVAN']">
															<xsl:value-of select="../cbc:DocumentType"/>
															<br />
														</xsl:for-each>
													</xsl:if>
													<xsl:for-each select="n1:Invoice/cac:AccountingSupplierParty/cac:Party">
														<xsl:if test="$varBranchName= '' or count(//n1:Invoice/cac:AccountingSupplierParty/cac:Party/cac:PartyIdentification/cbc:ID[@schemeID='VKN']) &gt;= 1">
															<xsl:if test="cac:PartyName">
																<xsl:value-of select="cac:PartyName/cbc:Name"/>
																<br/>
															</xsl:if>
														</xsl:if>
														<xsl:for-each select="cac:Person">
															<xsl:for-each select="cbc:Title">
																<xsl:apply-templates/>
																<xsl:text>&#160;</xsl:text>
															</xsl:for-each>
															<xsl:for-each select="cbc:FirstName">
																<xsl:apply-templates/>
																<xsl:text>&#160;</xsl:text>
															</xsl:for-each>
															<xsl:for-each select="cbc:MiddleName">
																<xsl:apply-templates/>
																<xsl:text>&#160;</xsl:text>
															</xsl:for-each>
															<xsl:for-each select="cbc:FamilyName">
																<xsl:apply-templates/>
																<xsl:text>&#160;</xsl:text>
															</xsl:for-each>
															<xsl:for-each select="cbc:NameSuffix">
																<xsl:apply-templates/>
															</xsl:for-each>
														</xsl:for-each>
													</xsl:for-each>
												</td>
											</tr>
											<tr align="left">
												<xsl:for-each select="n1:Invoice/cac:AccountingSupplierParty/cac:Party">
													<td align="left">
														<xsl:for-each select="cac:PostalAddress">
															<xsl:for-each select="cbc:StreetName">
																<xsl:apply-templates/>
																<xsl:text>&#160;</xsl:text>
															</xsl:for-each>
															<xsl:for-each select="cbc:BuildingName">
																<xsl:apply-templates/>
															</xsl:for-each>
															<xsl:if test="cbc:BuildingNumber">
																<xsl:text> No:</xsl:text>
																<xsl:for-each select="cbc:BuildingNumber">
																	<xsl:apply-templates/>
																</xsl:for-each>
																<xsl:text>&#160;</xsl:text>
															</xsl:if>
															<br/>
															<xsl:if test="cbc:Room">
																<xsl:text> Kapı No:</xsl:text>
																<xsl:for-each select="cbc:Room">
																	<xsl:apply-templates/>
																</xsl:for-each>
																<xsl:text>&#160;</xsl:text>
															</xsl:if>
															<br/>
															<xsl:for-each select="cbc:PostalZone">
																<xsl:apply-templates/>
																<xsl:text>&#160;</xsl:text>
															</xsl:for-each>
															<xsl:for-each select="cbc:CitySubdivisionName">
																<xsl:apply-templates/>
															</xsl:for-each>
															<xsl:text>/ </xsl:text>
															<xsl:for-each select="cbc:CityName">
																<xsl:apply-templates/>
																<xsl:text>&#160;</xsl:text>
															</xsl:for-each>
														</xsl:for-each>
													</td>
												</xsl:for-each>
											</tr>
											<xsl:if test="//n1:Invoice/cac:AccountingSupplierParty/cac:Party/cac:Contact/cbc:Telephone or //n1:Invoice/cac:AccountingSupplierParty/cac:Party/cac:Contact/cbc:Telefax">
												<tr align="left">
													<xsl:for-each select="n1:Invoice/cac:AccountingSupplierParty/cac:Party">
														<td align="left">
															<xsl:for-each select="cac:Contact">
																<xsl:if test="cbc:Telephone">
																	<xsl:text>Tel: </xsl:text>
																	<xsl:for-each select="cbc:Telephone">
																		<xsl:apply-templates/>
																	</xsl:for-each>
																</xsl:if>
																<xsl:if test="cbc:Telefax">
																	<xsl:text> Fax: </xsl:text>
																	<xsl:for-each select="cbc:Telefax">
																		<xsl:apply-templates/>
																	</xsl:for-each>
																</xsl:if>
																<xsl:text>&#160;</xsl:text>
															</xsl:for-each>
														</td>
													</xsl:for-each>
												</tr>
											</xsl:if>
											<xsl:for-each select="//n1:Invoice/cac:AccountingSupplierParty/cac:Party/cbc:WebsiteURI">
												<tr align="left">
													<td>
														<xsl:text>Web Sitesi: </xsl:text>
														<xsl:value-of select="."/>
													</td>
												</tr>
											</xsl:for-each>
											<xsl:for-each select="//n1:Invoice/cac:AccountingSupplierParty/cac:Party/cac:Contact/cbc:ElectronicMail">
												<tr align="left">
													<td>
														<xsl:text>E-Posta: </xsl:text>
														<xsl:value-of select="."/>
													</td>
												</tr>
											</xsl:for-each>
											<tr align="left">
												<xsl:for-each select="n1:Invoice/cac:AccountingSupplierParty/cac:Party">
													<td align="left">
														<xsl:text>Vergi Dairesi: </xsl:text>
														<xsl:for-each select="cac:PartyTaxScheme">
															<xsl:for-each select="cac:TaxScheme">
																<xsl:for-each select="cbc:Name">
																	<xsl:apply-templates/>
																</xsl:for-each>
															</xsl:for-each>
															<xsl:text>&#160; </xsl:text>
														</xsl:for-each>
													</td>
												</xsl:for-each>
											</tr>
											<xsl:for-each select="//n1:Invoice/cac:AccountingSupplierParty/cac:Party/cac:PartyIdentification">
												<tr align="left">
													<xsl:choose>
														<xsl:when test="cbc:ID/@schemeID = 'MERSISNO'">
															<td>
																<xsl:text>Mersis No: </xsl:text>
																<xsl:value-of select="cbc:ID"/>
															</td>
														</xsl:when>
														<xsl:when test="cbc:ID/@schemeID = 'TICARETSICILNO'">
															<td>
																<xsl:text>Ticaret Sicil No: </xsl:text>
																<xsl:value-of select="cbc:ID"/>
															</td>
														</xsl:when>
														<xsl:otherwise>
															<td>
																<xsl:value-of select="cbc:ID/@schemeID"/>
																<xsl:text>: </xsl:text>
																<xsl:value-of select="cbc:ID"/>
															</td>
														</xsl:otherwise>
													</xsl:choose>
												</tr>
											</xsl:for-each>

											<xsl:for-each select="//n1:Invoice/cac:AdditionalDocumentReference/cbc:DocumentType[text()='MESUL_MUDUR_AD_SOYAD']">
												<tr align="left">
													<td align="left">
														<xsl:if test="../cbc:DocumentType='MESUL_MUDUR_AD_SOYAD'">
															<xsl:text>Mesul Müdür: </xsl:text>
														</xsl:if>
														<xsl:if test="../cbc:DocumentType='MESUL_MUDUR_AD_SOYAD'">
															<xsl:value-of select="../cbc:DocumentTypeCode"/>
														</xsl:if>
													</td>
												</tr>
											</xsl:for-each>

											<xsl:if test="count(//n1:Invoice/cac:AdditionalDocumentReference/cbc:DocumentType[text()='MESUL_MUDUR_BELGE_NO']) &gt;= 1 and count(//n1:Invoice/cac:AdditionalDocumentReference/cbc:DocumentType[text()='MESUL_MUDUR_RUHSATNAME_TARIH']) &gt;= 1">
												<tr align="left">
													<td align="left">
														<xsl:for-each select="//n1:Invoice/cac:AdditionalDocumentReference/cbc:DocumentType[text()='MESUL_MUDUR_RUHSATNAME_TARIH']">
															<xsl:if test="../cbc:DocumentType='MESUL_MUDUR_RUHSATNAME_TARIH'">
																<xsl:text>Ruhsat Tarihi: </xsl:text>
															</xsl:if>
															<xsl:if test="../cbc:DocumentType='MESUL_MUDUR_RUHSATNAME_TARIH'">
																<xsl:value-of select="substring(../cbc:DocumentTypeCode,9,2)"/>-<xsl:value-of select="substring(../cbc:DocumentTypeCode,6,2)"/>-<xsl:value-of select="substring(../cbc:DocumentTypeCode,1,4)"/>
															</xsl:if>
														</xsl:for-each>
														<xsl:for-each select="//n1:Invoice/cac:AdditionalDocumentReference/cbc:DocumentType[text()='MESUL_MUDUR_BELGE_NO']">
															<xsl:if test="../cbc:DocumentType='MESUL_MUDUR_BELGE_NO'">
																<xsl:text> - Belge No: </xsl:text>
															</xsl:if>
															<xsl:if test="../cbc:DocumentType='MESUL_MUDUR_BELGE_NO'">
																<xsl:value-of select="../cbc:DocumentTypeCode"/>
															</xsl:if>
														</xsl:for-each>
													</td>
												</tr>
											</xsl:if>
										</tbody>
									</table>
									<hr/>
								</td>


								<!-- E-ARSIV FATURA LOGO -->
								<td style="width: 20%; text-align: center;">
									<img style="width:91px;" align="middle" alt="E-Fatura Logo"
										 src="data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/4QBoRXhpZgAASUkqAAgAAAADABIBAwABAAAAAQAAADEBAgAQAAAAMgAAAGmHBAABAAAAQgAAAAAAAABTaG90d2VsbCAwLjIyLjAAAgACoAkAAQAAAKYBAAADoAkAAQAAAKYBAAAAAAAA/+EJ9Gh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC8APD94cGFja2V0IGJlZ2luPSLvu78iIGlkPSJXNU0wTXBDZWhpSHpyZVN6TlRjemtjOWQiPz4gPHg6eG1wbWV0YSB4bWxuczp4PSJhZG9iZTpuczptZXRhLyIgeDp4bXB0az0iWE1QIENvcmUgNC40LjAtRXhpdjIiPiA8cmRmOlJERiB4bWxuczpyZGY9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkvMDIvMjItcmRmLXN5bnRheC1ucyMiPiA8cmRmOkRlc2NyaXB0aW9uIHJkZjphYm91dD0iIiB4bWxuczpleGlmPSJodHRwOi8vbnMuYWRvYmUuY29tL2V4aWYvMS4wLyIgeG1sbnM6dGlmZj0iaHR0cDovL25zLmFkb2JlLmNvbS90aWZmLzEuMC8iIGV4aWY6UGl4ZWxYRGltZW5zaW9uPSI0MjIiIGV4aWY6UGl4ZWxZRGltZW5zaW9uPSI0MjIiIHRpZmY6SW1hZ2VXaWR0aD0iNDIyIiB0aWZmOkltYWdlSGVpZ2h0PSI0MjIiIHRpZmY6T3JpZW50YXRpb249IjEiLz4gPC9yZGY6UkRGPiA8L3g6eG1wbWV0YT4gICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICA8P3hwYWNrZXQgZW5kPSJ3Ij8+/9sAQwADAgIDAgIDAwMDBAMDBAUIBQUEBAUKBwcGCAwKDAwLCgsLDQ4SEA0OEQ4LCxAWEBETFBUVFQwPFxgWFBgSFBUU/9sAQwEDBAQFBAUJBQUJFA0LDRQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQU/8AAEQgAaQBpAwEiAAIRAQMRAf/EAB8AAAEFAQEBAQEBAAAAAAAAAAABAgMEBQYHCAkKC//EALUQAAIBAwMCBAMFBQQEAAABfQECAwAEEQUSITFBBhNRYQcicRQygZGhCCNCscEVUtHwJDNicoIJChYXGBkaJSYnKCkqNDU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6g4SFhoeIiYqSk5SVlpeYmZqio6Slpqeoqaqys7S1tre4ubrCw8TFxsfIycrS09TV1tfY2drh4uPk5ebn6Onq8fLz9PX29/j5+v/EAB8BAAMBAQEBAQEBAQEAAAAAAAABAgMEBQYHCAkKC//EALURAAIBAgQEAwQHBQQEAAECdwABAgMRBAUhMQYSQVEHYXETIjKBCBRCkaGxwQkjM1LwFWJy0QoWJDThJfEXGBkaJicoKSo1Njc4OTpDREVGR0hJSlNUVVZXWFlaY2RlZmdoaWpzdHV2d3h5eoKDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uLj5OXm5+jp6vLz9PX29/j5+v/aAAwDAQACEQMRAD8A/VOiioL6+ttMsp7y8njtbSBGlmnmcIkaKMszMeAABkk0bgT1458QP2nfDvhbxDJ4W8N2F/8AEHxsvB0Hw6gla3PTNzMf3cC567jkelcJqHjHxT+1FJeL4Z1a48B/Bq03i88Vg+Tfa0qZ8wWpb/UwDBzMeTjj+IVTl+JHhz4QeArPT/gf4dtJ7SG/FtqEj6dcuVLQmSGaX7ssiT4wtyPMU/wiQkLXuUcCoO1Vc0/5dkv8T6P+6tel09DzqmIurwdl36v0X6/mdDdaJ8c/HdpJfeJ/GWh/B7QgNz2OhwpfXqIf4ZbubEaN/tRrisTSv2evhJ4v8XXnhrxD4w8W/EHxDaq7Twa9r94UOzZ5gTyzHG2wyR7lTOzeoYDIr1P4l/CeL41aDod415eeGNUjETuypuZ7dmjkmtJoyQGB2Lz1VlBHcHW0D4L+GfDPxC1Xxlp0E9vq2pl3uFWUiFncIHfb3J8tepIB3FQCzZFjeSD5ZcktdIpKz0teW7W/VsHQ5parmXdu/wCGy+4+KPi34e+Cvwt8W+NPDSfBfSr+60p7VNLaTUrkG/zBHcXhY7iV8qKRW4znPOK9b1f4H/Anwn4p1LQNHvPFPgTXtOsZdSdtB1bULYeVFGskjRu7NExVWUkD1I6g4+gfEHwW8EeK9VudS1bw5aX1/cGQy3Eu7e3mQJA/IPG6KKNDjsorD1/9m7wVr2peItQa3vbO/wBes7yyvZ7a8flLpY1nZEYsiMwhQZC9j611vNIzjCLqTTS195u706N7aN7dTH6m4tvli9dNLaa+W/8AkeYeFtE+Lek28M/gP4lP4th+wWuonw98RNM/exxTqWRDf24GZcKQV+bbwTwwJ6rw/wDtT2mka3beHfin4cvfhdr87eXBNqMizaVeN6Q3q/Jnvh9pGQOTVHx/8NvF1l4ss4fBPnpqOq+IV1m8164RFstPtY7B7RINgk3SMn7t1j27WYnJA3Yk8G+L734o+MvEnw08V+FYtY8L6bFNaTXWq+XLPN5TJHHLcIMAGf8AeSJhFwqBlLZ+XOfsq8eecVJWu2rRkvu0evdXfdFR56cuWLad+uqf6r5Ox7+jrKiujBkYZDA5BFOr5QdtX/Za8SX9p4K1R/Hfw/05EuNX8Dtci41bw9A+SJ7XJ3vDgE+U3IAyDySPpTwX400X4h+GLDxD4e1CHVNHvoxLBcwHIYdwR1BByCpwQQQRkV5NfCuilUi+aD2f6NdH+fRtHbSrKb5XpJdP8u/9XNuiiiuI6Ar5m8X3M37U/wARNR8IW9y9t8I/CtwE8R3sTlBrV6mG+wq4/wCWMfBlIPJwPQ13X7TfxD1Twd4FtdE8MMP+E18W3iaFovPMUsv37g+ixR7nz0BC5615L9v8P+GPDKfBnw7pZ8XeE7SyxfX3htxeX9ldQXCec9/aEDzElmOSiszOvmDYV5HuYGhKEPbr4nt5Jby9VtHzvbVI87EVE37N7Lfz7L/Py9To/EfirUNS+KZ8F6PpNv4T1rS7SCTw3GYhPb6rp5a4juIrpIgwhtD9nQKRypeFiMkR17N8P/hZoXw6tIYtMt2MsMBtIZ5yHlitfNeSO2V8AmKMyFUByQuBmsr4HfCWP4R+CLPSJboajfRhla4HmbIkLErDCJHdkiXsm4jJYjGcV6LXHia6b9lRfur8fPv52u92b0aTXvz3/IK+Zf2vv2s4/gnYL4e8NyQ3PjS6QPl1DpYRHo7joXP8Kn6njAPo/wC0d8cLH4D/AA5utcmEc+qz5t9Ns2P+unI4JHXav3mPoMdSK/IfxL4k1Hxdr1/rOr3cl9qV9M09xcSHJdiefoPQdAOBXw2dZo8JH2FF++/wX+Z/QfhlwLHiCs80zGN8NTdkn9uS6f4V17vTue6f8N7/ABl/6GC0/wDBbB/8RR/w3t8Zf+hgtP8AwWwf/EV88gV9ifsa/sejx6bXxx41tSPDiMH0/TZRj7eQf9Y4/wCeQPQfxf7v3vksJWzHGVVSpVZX9Xp5s/oTiDLeDuGsDLH47A0lFaJKEbyfSKVt3+C1eh6x+zL4o+P/AMaGg13X/EMWheDshll/suAT3w9IgU4X/bIx6A84+vJ45HtpEjlMUrIVWXaDtOODjoa8y8Y/tIfDH4XeILfwzrXiW00zUFCJ9kiid1twQNocopWMYxwxGBg9K9NtrmK8t4p4JEmhlUOkkbBldSMggjqCK/RsHGNKLpqpzyW93d39Oh/GHEdevjq8ca8EsNRn/DUYcsXHunZc77v7rI+PtE8Az/AL4gQeJ/HGpy3K27XN3ay2d0ss+vag8TrPcSeZGv2aPyNm6NphCrxxnICiti51K1+AOqad8WPBwkl+DfjDybrX9KjjIXS5JwPL1KGP+FTuUSoB3BweNv0Z478B6L8RNBfS9c0201S3DrNFHexeZGsqnKkgEEjPBGRuUsp4JFeA/DbT00Dxj4p0/wCKfivStd1TXZW0aHR5rZlmisnfy4FMccrxW9vMVbYpRSTJEGkZ2Ar7WniliIudTV2tKP8AMvJdGt79H5Oy/O5UXSkox23T7Pz/ACt1Ppu2uYb22iuLeVJoJUEkcsbBldSMggjqCO9S18//ALM+o3nw/wBd8T/BbWbmS5n8LFLvQbmc5e60aUnyee5hYGInpwor6Arw8RR9hUcL3W6fdPVP7j0aVT2kFLZ9fXqfPujIPib+2HrmoS/vdL+HOjxadaKeVGoXo8yaRT6rCqIfTdXp9z4K8I6t8RYtZ/s5I/F2mQpI1/brJBI8UgkRUkdcLMvyP8jFgCAcDg185fCLwrrvjv4f6x400S2g1W5vviPqHiGXSrq9e0j1G3haS3hhMqq2PLZI5FDAqWiAPByPoL4O2fiCHSdcvfEMipPqOrz3dvpyagb4adGQim387AziRJX2jhPM2DhRXp42PsnaM7ciUbX+/wA9Xd7W13vocdB8+8d3e/5fojvqQkAEk4Apa8a/a6+I7/DL4DeI7+3l8rUL2MabaMDgiSX5SR7qm9h/u187WqxoU5VZbJXPosuwNXM8ZRwVH4qklFerdvwPz3/a++Nknxm+Ld9Lazl/D+kFrHTUB+VlU/PKPd2Gc/3Qo7V4dSk5NPghe5mjiiRpJXYKiKMliTgAe9fjVetPE1ZVZ7tn+leV5bh8mwNLA4ZWhTikvlu35t6vzPe/2Pf2eG+OPj/7RqcLf8Ino5Wa/PIFwx+5AD/tYy2Oig9CRX6ZfEfxEnw3+F/iLWrSCONdG0ue4t4FXCAxxkogA6DIAxXP/s6/Ci2+C3wm0Tw8FRdQ8sXOoSDGZLlwC/PcDhB7IK7Lxn4bs/G3hHWvD95JttdUs5bOVlIyqyIVJHuM5r9Oy7A/UsLyx+OS19ei+R/DHGfFS4mz5VarbwtKXLFd4p+9L1la/pZdD8SNV1S71vU7rUL+eS6vbqVp555TlpHY5ZifUkmv1v8A2P7m9u/2bfAz6gzNOLNkUuefKWV1i/DYFr4y8N/8E8fH9547GnaxPYWXhuKb95q8NwrmaIH/AJZx/eDEdmAA9T3/AEg8PaDZeFtC0/R9NhFvp9hbpbW8Q/gjRQqj8hXkZDgsRQq1KtZNaW1667n6L4s8T5RmmBwuX5ZUjUafPeO0VytJeTd9ultbaGhXgP7Q/g/RdD1jSvHz6fpE+p200apJrt9cR2cdwvMMwtoI3a5nGAqjggKMHgY9+rmPiWryeCNVSK6ns7howIZLW+SylaTcNqJM4IQscLnH8XHNffYWo6VVNddHrbRn8v1oKcGjwb4n63eaTqXwP+M11YTaPe/aYdD1+2miaFktL9Qp8xW+ZVjnCMFbkbuea+ntwr4+8T6HonjP9lH4ry2N5p93qklnLcmWx8XzeIpGazUXCb5pMbJAwJ2IMAFTnnjiP+Hg8v8Aeh/Svell9bG00qEbuDcflo136trfZHnRxMKEm5v4rP57P8kdx+y7oHj/AFX4LfCu78Ha5ZaJYQ2niBdSfU7R7yCSd9UQxAwJPES4CXGHyQo3DHzivqbwXpGoaH4dt7XVptOuNT3yy3E+k2Js7eR3kZyyxF3Kk7ssSxy2498V4/8AsZn+y/h74p8LtxJ4Z8W6vpZX0X7QZlP0KzAj6175XnZnWlPEVIWVuZtaa6tta79TpwkEqUZdbL8kv0Cvh7/gpz4keLRvA2gI/wAk9xc30i+6KiIf/Ij19w1+eX/BTcufHXgsHPl/2dNj6+aM/wBK+LzuTjgKlutvzR+yeF1CNfizCc/2ed/NQlb8dT4ur2n9jvwUnjr9obwnaTxiS0s521GYEZGIVLrn2LhB+NeLV9c/8E1LBJ/jNr90wy1vocgX2LTw8/kP1r87y2mquMpQe11+Gp/ZHGuMngOHMdXpu0lTkl5OXu3+VzqP26vhv8RPiV8X7STw94U1jVNH0/TIrdLi0gZo3kLO7kEf7yj/AIDXxz4o8O674K1mbSNdsrrStThCmS0ugUkQMAy5HbIIP41+4dfjh+054k/4Sz4/+O9QDb0/tSW2RvVYcQr+kYr6DPsFCh/tCk3Kb26H5B4T8TYnNUsmlQhGlh6fxK/M3dWvd21u2dd+xBo8mv8A7SfhbeWeKzFxeOCScbIX2n/vorX6w1+cP/BNLQftnxX8Sasy5Wx0jyQcdGllTH6RtX6PV7fD8OXBcz6t/wCX6H5f4wYlVuJfYx2p04x++8v/AG5BXE/GL4dWnxP8C3ujXUl5HgrcxGwEJmMiZIVRMDGd3K/MMfNnIxkdtRX1MJypyU47o/DpRU4uL2Z8xaH8N20L4XfEjVNb0vxVaan/AMI9c2aXPimbTC7W4tWUpGLBtmwBEyJOcgEdzX46ea3qfzr90f2rfES+Fv2b/iNfswUnRbi1Q/7cy+Sn47pBXxR/w781T/nxH5Gv0nh7NKWGp1a2JdudpL/t1a/mj5bMsHOrKEKWvKvzf/APpZRqvw7/AGjfif4e0Z0trvx54fXX9AeXHlLqVvEYJk54JP7mQ54xXoXwV07xPazXt1qy6vaaXcQqYrHxBqAu7xZlmlBkJGRGrxeSSgOA2QAMZOV+1L4O1W+8L6P468MW5uPF/gW8/tmyhT711AF23VrxziSLPA5JVRWP4cTRLvXLH4ueFf7X8W3fiy13WFjaxqEVSiArPO3ESRkMNpIwcgK7KK/OsfF1I0sYtbe7LyaVk/nG3q79j7/KqkXSxGXSsnL3otq7fXlvdKKvd8z+Fdrs+g6+F/8Agp1oDNaeA9bVfkR7qzkb3YRug/8AHXr7V0DWU1my3GS2e8gIhvI7SbzY4Z9qsyB8DONw5wPoOleJftzeBW8bfs9a1LDH5l1oskeqxgDnahKyflG7n8K8LNKft8FUjHtf7tf0PrOBcb/ZPE+DrVdFz8r/AO304/d71z8oa+tP+CbGpLa/GzWbRiAbrQ5dvuVmhOPyz+VfJhr2P9kLxingj9obwdeTSeXbXN0dPlJOBidTGufYMyn8K/M8uqKli6U33X46H9v8Z4OWP4dx2Hhq3Tk16xXMl87H62a7q0Wg6JqGp3BxBZ28lxIfRUUsf0FfhzqV9Lqmo3N5O26e4laaRvVmJJ/U1+vX7WHiT/hFf2dvHV5u2PLp7WSnvmdhDx/38r8fB1r6TiWpepTpdk39/wDwx+MeCGC5cHjca18UoxX/AG6m3/6Uj9Bv+CY/h/yPCXjbWyv/AB9XsFmrY/55Rs5/9HCvtevm/wD4J/aF/ZH7OWnXO3a2p391dk+uH8ofpFX0hX1OVU/Z4KlHyv8Afr+p+C8e4v67xPjqt9puP/gCUf0CuH+KPjy28IWFvZzWWrXU2q77aBtJVRKH25IR3KqHCCRwM5PlnGTgHtycCvJbnVj4/wBUlstbtbGz0+xiD614X8T2CSoI1LEXUE/3HXjr8y/LzsYGu6tJ25Y7v+v6/I+Vy+lCVT2tZXhDV6/dtrv6K9k5K6PKPiP4hs/i5p3wp+H2leIb3xTbeJ9fXUr+41G3WCddNsSJ5Y5UWNMEuIlBKjOe/Wvq/wApfQV82fss+GrPxj4t8T/Fm208afoV4G0TwpbFSuzTY5WeW4weczzln55wo7Yr6Wr1cTF0YU8LLeC97/E9X92i+R5U5069eriKSajJvlva/L0vZJeeitqJ1r5Y1jT4/wBmPxpqWl6g1xb/AAT8bXLH7TbTPD/wjmoyn51LoQY7eY8hgQEY44Byfqis3xH4c0zxdoV9o2s2UOpaXexNBcWtwu5JEPUEf5xUYetGneFRXhLRr9V5rp92zZnOMrqdN2lHVM5rwNoGuaHf3Ee7R9P8JRIbfTNF023JaGNT8kpmyAS4LFk24Hy4YncW2v7U0fxe+uaEHW+S3X7JfxhSYwZEOYi3TdtIJXqAy56ivnk3niv9keGXS9SfU/FHwbZSlnrdsv2jU/DCngJMuCZrdOqvglAMEEYB6DTLfXbhvDdp8MdaEngO9iiY67Zm2ulkZmle8nuJHzIZmxGEKjG9239MDmxWHlhIxlBc9N7Nflbo+6e3TTU9vBzhmdSbq1FTqpJ66LTd3Sbk+1ruTbbd1Z/CPjn9kf4k+HvGOs6bpnhDV9W022upI7W+t7Yuk8W47HBHquM++ax7b9mr4uWdxFPB4D8QRTROHR1tGBVgcgj8a/UTwt8dvDHie11+88+TTdM0dofN1G/Ait5Y5c+VIjk/dbgjODhlPRhXf2t5BfQRT280c8MqLJHJEwZXQjIYEdQR0NfGLh/CVHzQqP5WP3qfi9n+CgqGKwcLpJNtS1dk9dbXaabXmfLH7Ulr45+Kn7MPhqz07wrqkviLU7i1fVNNSAiS32I5k3L6eYq49QQa+If+GXPiz/0IGuf+Apr9hbi7gtQhmmSISOI03sF3MeijPUn0rF8XePND8CwW8utXjW32gsIY4oJJ5JNq7m2pGrMcLknA4AzXdjcoo4ufta1RqyS6Hy/DHiLmPD+GeX5dhISUpykl7zevRWetkkvRHOfs9+ErjwL8E/BmiXlu1re22mxG4gcYaOVhvdSPUMxBr0JmCgkkADnmuR1T4r+GtI1Pw7Y3F8wk1/Z9glWFzDJvH7vL42jd0AJycivH9evL342DxFoeuLL4E13w5L9qt9RWZVhNoXKyxu5Yh0IjyzYAGY2xkc+sqkaMI0qXvNaJei/yPz14TEZliamNxn7uM25Sk1tzSabS3aUtHa9vz634h+L4vHWv6n8NLRr/AEbV2jjnhvLi3Js73ad7QOUO9Y2ClSw2kgNgnGG828VPqPxg1OH4HeGNVvbjQdNC/wDCb+IjcGZreAncNLinwC8jfcLH5lRfmyxYU6Txtrvx11N9A+FFwfsUUX9na38W7q0jSR4g2WgsSqqJZMk/OoCKeRyQa9++GPwx8P8Awi8IWnhzw5afZrGDLvJId01xKfvyyv1d2PJJ+gwAAPco0f7Pbr1/4r+Ffyro5ea6L5vpfwcXjI4ulHB4ZWpLWT/mlazadk7O3Xbpvpv6PpFnoGk2emadbR2dhZwpb29vCu1Io1AVVUdgAAKuUUVwttu7OZK2iCiiikMa6LIhVgGVhggjIIrwnxD+y8NA1y68SfCXxHP8NdcuH825sLeIT6PfN6zWhwqk9N8e0jJOCa94oroo4iph23Te+63T9U9H8zKdOFT4l/n958uT+MPF/ga3Nl8RvgvLeWIv4tSm1v4cAXltc3ERUpLLa/LMMFEJ3bvuj0qj4c+NvwXuvi/qfjFviTb6Tqd3bmA6br1tPYS2zeXHHsLSlF8seXu2bfvOx3dMfWNfOn7YX/Iqx/7hrso0sHjasYVKXK77xdlf0af4NI1+v47BU5unWbTTTTV9Ha6v52XnoZfgnxZ4P0HwVbabe/G3wjqM9vrttqa3T+IonP2eNoy8RZpOS2x+w+98xY7naT46fHD4HeM9N0uzv/iXoTzWF8LuNbGIat5v7t42jMUYcMGWQ8EEZA4Nfmrqf/IeH+9/Wvvr9h/oP9w/yr3Mbw5g8BhueTlJW2ul+NmctHiXH4nFqtFqM027pdXo9PToa2neNJfFmk+HNO+H3we8R+M20OD7PY+IPGoGl2IXKMJD5mGmAaNGCiMbSi7cYGOtg/Zp8QfFHUU1X40+KU8QxAqy+E9ARrPSE2klRKc+bc4JJG8gDJ4wa+hx0FLXzscTGhphaah57y+97fJI6KrrYp3xVRz30e2ru9PN6+pU0vSrLQ9Ot7DTrSCwsbdBHDbW0YjjjUdFVRwAPQVbooribbd2VtogooopAf/Z"/>
									<h1 style="text-align: center;">
										<span style="font-weight:bold; ">
											<xsl:choose>
												<xsl:when test="//n1:Invoice/cbc:ProfileID='EARSIVFATURA' or //n1:Invoice/cbc:ProfileID='EBELGE'">
													<xsl:text>e-Arşiv Fatura</xsl:text>
												</xsl:when>
												<xsl:when test="//n1:Invoice/cbc:ProfileID='EGIDERPUSULASI'">
													<xsl:text>e-Gider Pusulası</xsl:text>
												</xsl:when>
												<xsl:otherwise>
													<xsl:text>e-FATURA</xsl:text>
												</xsl:otherwise>
											</xsl:choose>
										</span>
									</h1>
								</td>

								<!-- FIRMA LOGOSU -->
								<td style="width: 40%; text-align: center;">
									<table style="width: 100%;">
										<tbody>
											<tr align="right">
												<td align="right">
													<div id="qrcode" style="float:right; margin-top: -6px;"/>
												</td>
											</tr>
											<tr align="right">
												<td align="right">
													<img src="data:image/jpeg;base64, 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" alt="company_logo" width="175" height="125"/>
												</td>
											</tr>
										</tbody>
									</table>
								</td>
							</tr>
						</tbody>
					</table>


					<!-- ALICI - IMZA - FATURA BILGILERI TABLOSU -->
					<table>
						<tbody>
							<tr>
								<td style="width: 40%;">
									<table id="customerPartyTable" align="left" border="0">
										<tbody>
											<tr>
												<td>
													<hr/>
													<table align="center" border="0">
														<tbody>
															<tr>
																<xsl:for-each select="n1:Invoice/cac:AccountingCustomerParty/cac:Party">
																	<td style="width:469px; " align="left">
																		<span style="font-weight:bold; ">
																			<xsl:text>SAYIN</xsl:text>
																		</span>
																	</td>
																</xsl:for-each>
															</tr>
															<tr>
																<xsl:choose>
																	<xsl:when test="n1:Invoice/cac:BuyerCustomerParty/cac:Party/cac:PartyIdentification/cbc:ID[@schemeID='PARTYTYPE' and text()='TAXFREE']">
																		<xsl:for-each select="n1:Invoice/cac:BuyerCustomerParty/cac:Party">
																			<xsl:call-template name="Party_Title">
																				<xsl:with-param name="PartyType">TAXFREE</xsl:with-param>
																			</xsl:call-template>
																		</xsl:for-each>
																	</xsl:when>
																	<xsl:when test="n1:Invoice/cac:BuyerCustomerParty/cac:Party/cac:PartyIdentification/cbc:ID[@schemeID='PARTYTYPE' and starts-with(text(), 'EXPORT')]">
																		<xsl:for-each select="n1:Invoice/cac:BuyerCustomerParty/cac:Party">
																			<xsl:call-template name="Party_Title">
																				<xsl:with-param name="PartyType">EXPORT</xsl:with-param>
																			</xsl:call-template>
																		</xsl:for-each>
																	</xsl:when>
																	<xsl:otherwise>
																		<xsl:for-each select="n1:Invoice/cac:AccountingCustomerParty/cac:Party">
																			<xsl:call-template name="Party_Title">
																				<xsl:with-param name="PartyType">OTHER</xsl:with-param>
																			</xsl:call-template>
																		</xsl:for-each>
																	</xsl:otherwise>
																</xsl:choose>
															</tr>
															<xsl:choose>
																<xsl:when test="n1:Invoice/cac:BuyerCustomerParty/cac:Party/cac:PartyIdentification/cbc:ID[@schemeID='PARTYTYPE' and text()='TAXFREE']">
																	<xsl:for-each select="n1:Invoice/cac:BuyerCustomerParty/cac:Party">
																		<tr>
																			<xsl:call-template name="Party_Adress">
																				<xsl:with-param name="PartyType">TAXFREE</xsl:with-param>
																			</xsl:call-template>
																		</tr>
																		<xsl:call-template name="Party_Other">
																			<xsl:with-param name="PartyType">TAXFREE</xsl:with-param>
																		</xsl:call-template>
																	</xsl:for-each>
																</xsl:when>
																<xsl:when test="n1:Invoice/cac:BuyerCustomerParty/cac:Party/cac:PartyIdentification/cbc:ID[@schemeID='PARTYTYPE' and starts-with(text(), 'EXPORT')]">
																	<xsl:for-each select="n1:Invoice/cac:BuyerCustomerParty/cac:Party">
																		<tr>
																			<xsl:call-template name="Party_Adress">
																				<xsl:with-param name="PartyType">EXPORT</xsl:with-param>
																			</xsl:call-template>
																		</tr>
																		<xsl:call-template name="Party_Other">
																			<xsl:with-param name="PartyType">EXPORT</xsl:with-param>
																		</xsl:call-template>
																	</xsl:for-each>
																</xsl:when>
																<xsl:otherwise>
																	<xsl:for-each select="n1:Invoice/cac:AccountingCustomerParty/cac:Party">
																		<tr>
																			<xsl:call-template name="Party_Adress">
																				<xsl:with-param name="PartyType">OTHER</xsl:with-param>
																			</xsl:call-template>
																		</tr>
																		<xsl:call-template name="Party_Other">
																			<xsl:with-param name="PartyType">OTHER</xsl:with-param>
																		</xsl:call-template>
																	</xsl:for-each>
																</xsl:otherwise>
															</xsl:choose>

															<xsl:if test="$varSenaryoName='1' and not($varVknComp='1')">
																<tr align="left">
																	<td style="width:469px; " align="left">
																		<span style="font-weight:bold; ">
																			<br> </br>
																			<xsl:text> Ödeme Yapacak Kurum </xsl:text>
																		</span>
																	</td>
																</tr>
																<tr align="left">
																	<td>
																		<xsl:text> VKN: </xsl:text>
																		<xsl:value-of select="n1:Invoice/cac:BuyerCustomerParty/cac:Party/cac:PartyIdentification/cbc:ID[@schemeID='VKN']"/>
																	</td>
																</tr>
																<tr align="left">
																	<td>
																		<xsl:text> Ünvan: </xsl:text>
																		<xsl:value-of select="n1:Invoice/cac:BuyerCustomerParty/cac:Party/cac:PartyName/cbc:Name"/>
																	</td>
																</tr>
																<tr align="left">
																	<td>
																		<xsl:text> Adres: </xsl:text>
																		<xsl:value-of select="n1:Invoice/cac:BuyerCustomerParty/cac:Party/cac:PostalAddress/cbc:CityName"/>
																		<xsl:text>/ </xsl:text>
																		<xsl:value-of select="n1:Invoice/cac:BuyerCustomerParty/cac:Party/cac:PostalAddress/cac:Country/cbc:Name"/>
																	</td>
																</tr>
															</xsl:if>
														</tbody>
													</table>
													<hr/>
												</td>
											</tr>
										</tbody>
									</table>
								</td>

								<td style="width: 30%; text-align: center;">
									<img src="data:image/jpeg;base64, /9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAIBAQIBAQICAgICAgICAwUDAwMDAwYEBAMFBwYHBwcGBwcICQsJCAgKCAcHCg0KCgsMDAwMBwkODw0MDgsMDAz/2wBDAQICAgMDAwYDAwYMCAcIDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAz/wAARCADoAUYDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwD95bi4k+3ECR8biMbuBzTGu3Vv9ZJj/fpZ4f8AS35H3yf1qN7dh0Ix396sCU38pJG5sDuCaRr+UYwznP8AtGgQlR2oWPaR60wEe/kWLc0jjnH3jSG+kQ/6xzu/2jxQ9vvDZ6E5oeHIBC9PegCwJpAn33/OopLuUSbVdj77qCxxjH60mzJ60AL9smIHzH35NK11K2cO/wCZpuzIxQEK/jQAC7kJAMj/APfVOF5Jn77/APfVMMJYcUoTb9RQArXsny4Z+c9zTVv5HbG9/wAzTfLKOcnAP6UC1wM7vxxQA7+0JcD5zgnH3qPtU3Pzvx1+bpSC0+QemaXyMu3vjNAD47mQoP3j/wDfVIbiVZP9Y/TP3qQLtGBTUHzHP0oAZHd3G7mR+f8AaP8AjUn2qQjmVx9GNGwY6UjoAtADftk0fAlc892NRLqE3ynzZOvPzHipliXOetNe2G3AApuwDZ7qebASaQd8hj/jTjdzbT+9k6f3jT0iCr0ppTikAn2ubj97Jz/tGpY55FXPnSH6saYsQIGaANpoAjF5KW/10n/fZpBdzHkTS8HpvPNO8kA0CEAU1YBEvJ5Hb95IMf7RpPt0xYfvJP8Avo1IEA/Gk2Kv07U7oBDey8fvZOv9403UvEMOg2LXN9fQ2dqmN89zOIo0ycDLMQByQOtZfjzxlpvw38G6r4g1iZoNL0S0kvruRI2dkiRSzEKBknjoK+YvFmv3P/BUb4Z6voPhTXNX8HeDxdoz6tb3EsF5OkcrhNqwvFKoeSAsR5owvBz90606EqidTaK3YHtvhj9t34R+N/EQ0fRvij4R1PVTL5P2a21SN2Mm4Js4bGdxA/GvTDcyoTl5M44GTXwd+1x/wT/+F37Kn7NN14h8A6InhnxJokx1P+1ku7ua7uZIbWaTl5JXYZkiR8EkZXJB7/anwv12bxZ4F0/ULrJnuFk35OekrqOmOwHatq+FpxpRxFJtxbtr5AbbXcwj+/Jn/eNV9Uv7+C2L2itcSgg+WZMZGRkZz6Zq4IRmjbh/xrhARZ5gmC7j6sc0n2mUD/WP/wB9GnlcvSGNR1pgNFxI/PmycdtxpGu5lb77/wDfRpyICOlPKA9qAGLcyN/y0f8A76NFKyBeRRQBLP8A69/940wr82afcnEr/wC8aYpyKQATgUA5FBGaAMUwFoxRRQAi/MKAc0oYr0pO9ACk4FIpyKWkAxQAA5oZsUjHaf1pxUECgBpHJNLj5M4oIyKXquKAGu+4CkVttLIm0Cm0ABOTTfMAagthq4340fFez+E3hxLq6Esk17J9ltIo49xlmKsVXkgDJXGSQOaai5PljqwNPUvjF4S0HxlaeG7/AMTaBZeItQ2m10ue/iju7gNnGyIsGOcHGBziujzuPr/WvmDXf2FbL40fDbWdR8c2SyfETUAJ7S7t71o49OltirWgVU/dkCSNXbesmd7A8YUesfspX2o/8KasdJ1eQTal4Zkl0SeRQoEn2ZzGrfKADlAvIA+grepRjyt03ezs/wDgeQHpLmkH7xaD0pF+WPiucBgGKU80UwsTQA+ml8GkU80rDAoAPMpoORRRQAjNtpks2xc46UTOF618xf8ABUH9rO5/Zs+DFhpmjEHxL4+uptD06NrcSht8DruyxCKfMeHBYkcnIxmt8Nh5V6saUN2B59+0Z8Wk/b0/aY0f4IeE9Qju/BWny2mueJdV09mlWSODMrWzZKwsrGS1Ug7/AL/3Tj5fsX4a/D/TfhZ4C0nw5pFtDa6bo1sltAkUSRghRyxVQFyTknAHLH1ryD/gnf8Asc2/7F37O9r4YkZptYkvLm8vrg3PnB2kcBQCFRceXHF0Ucg+pr3o8JXVj68JS+r0P4cevd9/n+QHyp/wVj1a71D4a+BfCFhEZ7nxp4mj0+REUs4gaJ4XYAcHBnXrxyK+rNI0mHQdOitIBiKHO0AAdSSenHU186/ELSI/jb+3j4WsIm3J8P8AQzqlxuJj2yvqMKrg4+b/AI9X46cDnmvpBHz9KnEPloUqPa7fz2/AB9NZske1OzTP4/xrgAfUcgzmnFuKCMrmgAi6U6mKMMKcKABhuFFBOKKAH3BxM/8AvGo/MpbuTZM+f7x/nUanJ9qQEitmlpiuM5HSgy+lMB9FNibzKa82xqAF27Wp9QzXOyRR/Ske5+bgdqAJCtJUb3Wce9SA57YoAcGyKQHbUcj4baOtRwyuQ+8gkHt6c0AWd9I5zTC58rI61D5krDJ6e1AE/Sgtg1VScgg9ieKsF8xc07MBJSx4XGa8K8QaBefGn9qqxs4LsW2keB7FdRuXKtL9quXvMCEAEKuFt35OWG8fLjNew+K/FMHhTw9cX05by7bbnaueCwUcfVq8f/Yl8K69pvhfxF4k8S/ZBqXi7UBewG2bKi1ZPMjDDoG3TSZ69ueK7KC5aMq3XZfPf8APcYwIV2/jXC/DRofD/wATPFOk+cJJrq6k1XAI+RZFh4I65yevoRXbmbMg2nnHfvXlHhjWbmT9sbWrNzD5A0YSIADvz+56npjrUYWHNGV+1xHsNGagmvfJUHk84OKeZwv1rlGOftSFuKYZ1fpnd3piz8HP6UATBwKTqaiFwSOO1NeclffvTswJzxULzbGHelikyvHcVVupiBsHA71QE7SqeZHSNR1ZjgCvh79kvxUv/BQb9snxR8S761S38LfDE/8ACO6Fbv8A6R9ouRfG5+0EnMany44QfLO75uuMV6N/wVM+PD/Av9mGRbR/+Jx4lvoLGxUw+Yp2OJ5CckAfJEevr09Oz/Yn/Zb0L9kv9n/SfDeiR3Ecl0kN/qZluDP5l41tDHKQSAAP3Q4AAr1KCVDCyrJ+9N2j6df8guj2rfz7+vWnxgyNjjHvVXztp46d65H49/FSP4QfCjVfEEuQlj5K8R7+XmROmR/erzaVJykqa30QHkH7BGs3HxG+Kfxe8YXELW//ABPH0W3VgTuiimnm3Kx7HzhwOOK+nV5FeJfsI+Bm8A/s96W0qbLnXlh1ab594Z5baHJHpyDxXs4uSO1b49qVeTW2i+5AWEbac0vmDOahbMqqRT4/mQ1xgK7gLTA/mCkLljiozKfM2jGFPOaALAOABQo8t+elR79350ruWB5wcUASM25qKrxLKr5Z9y44GP8A61FAElx/x+S8fxH+tNjHIB5qxO2J5B/tGoFwZtvQgZpAB+UH3pVfctObcen8qQoT160wHIQI+agmieVyQRjPFTD5U29KBx3zQBGzZlUlc49qV+PmAwD2qTNKZcjmgCvNGrwLx845zT4bjzEBIxzjmpByfSklIQ/WgCKQ5lzznpS42uy9u1OPAzSmcIM59ulADVUquKagMZI7H2p7T7e/NN80yU07ARPEzhR71K8YK4HSguqrzxUb3Kp1P4UXvowPDP8AgoIs+p/AWfR7PVW0a61S9t0FynLKFJkIxkEg+V617F4L8OR+GPCWmaagUJp9nFbLgcEIgX+leM+MRH8Q/wBtXR9HdisGkaYbuRlU5JMcygH2/fDp3A9697kmw5zwc/n7124lqNGnS+f3gVpYdpU4HGe9eXeHrGRv2uNWufKIiXSFAk525/c8enevVLicLIq43bjxiuH8EW9vqfxv8S3cUzObZRZyR7fljcR27EZx1wR+dThpNRl6E9TtYLG5TUJJWuN0LKAkQXGw5JJz9CB+FTyxNu+lTKAlN8wMK4yiFYsLu7+lKqYTpinSyCIZB596QS5Xt9PSgBjxsq7ufpUYhymR8rHk1O0wZcA1EZMVV2ArIfL9wOKrzAzJtIwT7dKlM/Y/WvPv2ofilH8Hf2ffGPiQywQtpWlTyQmc4QzFCsak+7sox71pRhKpNU47vT7xWPmoagn7V/8AwVBl8N6gqXnhv4R217LPazt5sUk09vbwKQFxtIYyH5z64Gen2k8B3semTnAFfLX/AAS2+Eo0n4f6z8UL1idc+KUrajOMjylT7VcumwAkYKuh7Hj619TmdfMwHHSvSzaUfbqhT+GmlH59X99x2GmFi2Bx7184f8FPLS+8QfBHRPCunt/pXinWUgyGK/JDDNcN90FjzEvT2zX0qynb0/Wvnjx1rEfxT/b08F+HUlSa38EWWp6jeRx8tbtLa20ce88EZ+0Njrn8OMsvuq/tP5Fzfd/wRWPf9E0gaNpFpZIqrHaW6W6KvRQqhRj24q55OxeOtI11uk9Sad5u6SvOlrqhipkLTwDmmlxuxThJ3FSArrlenPtVZ1uN+QEI9Cef5VY3Gk88KeWAoArXKXLR/IUDnG3PReee1LJFcGTKmPA5PuPyqwzn8O9KrEED9KAKUcd8LlyzQ+SfuDOCPr8v9aKuSSYbFFAC3RP21+f4j/OmEf6Zuz/DU11H/pT8/wAR/nTRGF7/AI0gGCU7RzjPejcW6NnBqVUXbjIOKTyghGKYEbhvvZ/CnZLA/SnMuaFG3pQBGG3ADNEgKqOc+9PMYyOetDQg8ZoAcAcVHcDletTeYAKa2GwT2oAjyfK79aayh416etTH5lpNooAjYLuPQ0sJQjA4PvQyqWwOtKUEcfv70AR3RBTtkc1BcIGnjOQF7g/WrEigjkdO/rWd4tvV03wtqN1t3fZbWWYZ/wBlCf6Vcd0gPA/gVcTeMP23/iPqzXcM1noxk0mGAKpeNkjss/MO3zt8p9a+hy3mE5J49a8l/Y+8OW0HhnxNriqpuvEHiO/u5DsClQXVAuepwI15P5V6/KFDYPHpXZj2vbci+ykvuQehCzBZIwcE56/jXN/DLSvI8ReJ70eXi61SXJEYViQkSckdfuVv6ufLsbhk+Z0iZgPU4OBXP/BiC5t/Dd693uWS41O7lVCc7UMxxjn2z+Nc8dISkL1OtuAxIxn3qM/L689SasZ+Wo+GTORWAyBxuz3FKiBenPHWnggjtS7wo4/SmgIFiI2549aZNkrgepGfxqy82eDj3NQEqHPORnNWJla5YxvgH/69fMX/AAVM1Vte+Bej+BbdZZb/AMc+JtL0rykkI3RSTFm3BfnK/ujnAr6jmZAx5Ge2RXxl4z8Sw/F//gsP4X0GO4juNN8EaKuoPHEpkCTrDO6ls/KpH2pCCBn7vPNenlNJ/WHW/kTl92wtT6W/Z8+HyfCn4HeEfDaRLCujaRbWzRruwriNd/3vm+9nrzXaeUDcrtHbnHfmrLuFbtzSF0QjJ2nsPWvPnUlObnLq7iuOnlW3iaRzhI1LMSegHJNfKH7INk/jH9un47eMWnM1rFLBpForHOwI7RPtI+XGbQdOenoa93/aR8X/APCG/ATxfqCypDLFpNwsbMSMOyFVxjBzkjGO9cp+wV4JTwn+zxo95M7SX/iMz6pcu6YLGe6nuF9SeJuMknFd1C9PC1Ki+1aP6/oWexONuGGOKdGm5w1IYlc/e6frT4tpHWvMewDmGOlKBtpSRjg0Z5qQAHJqOSLcOnIPXFTBlHelEuPSgCPBK8Hj0NKFO/NPE4A5AFIZMt7UAMKdc+tFOZgRRQA+6i8y7f5sfMf51Ecp945I7VJcIwupCDn5j/Ok25HPX3pANIKAEfjT2XC554FDDcKV23rxTAhWXJxk0vmblUDrTkjw2TzSiMA5oAJm2EUx5CGwO/OadIfOPpQ4xj2oAjkkxJjuOtK5L7cH1p6xDLevrSCLb3/GgCNBIJ/vcY4FKkjb+TTyuZfbGKSSOgBjTDz+Kkk+Yf4mmCLDZzT93GKAIY5MISTmuV+K+rrafDPXyd/zafOvynBGUYf1rqZYg68vtxXAftFSwx/DC+tnIQ3aLEI4/wDWy5kQHYo5Y89AD2rfDpOpFMVyH9ljS/7B+Cmn/vjM13cXN1kg5AkmdgpznJAwM+1ehTz7mH6e1YXwi01NL+F2g26rIAljFgSpsdcqD8wIBB55yBW5exk4x0HXFOu3KrOT7iTtoc/8UPES+Ffhzr+pNK4Wy024nLoPmG2Njke4xWX+zprLeIPhBpWoySyzHUVkukeT7xR5GZc/gRV343QPJ8HfE/lnEjaZPGpxnBZGA/nUP7PmmHTPgp4bjYYf7ChfjGWPJOK0slhvV/oVc7cv+6x7VDGSkRHXmputNMfzetciVwIlGfx/SlPyj60OPnOR3oVBk4NWl0ArXbOWwvpzz0qJJPJKk8gDkVJf3kNohaWeKAEZy7hen1/zzVZZ4ruLMciSRsMh1bIP400n2Jeo3V9Rj02wuruT/VWsLzvx0Cgk18Z/8EptAm+M/jLxZ8atThha91iaXR4ZJcNcIscFivUYGP3bds8167/wUU+KK/Cb9k3xPcLMI7jVbK606DDsrtI9ncEBdvJbKjAp/wDwTW+F958Hf2P/AAzo9+l1FfGa8uLhbhdsis11KFz/AMAC9e1e5RSoZdOfWbUV6at/oV0PeLpvLmQf3un5VVnuxcT4Vj8ntVi4Czrg8kdMVA1za6LZzT3EscESKXkkkIVUUDJJP5/lXha9CDxn9t7WYdQ+H2geFfNkjufGXiKw0rcASvlu7OwbpxiFu/pXrXw88Mx+C/h5oekQFMaRYQWgKrgHZGq9OfSvlz4n+Mn+KX/BTz4f+FrQfbNK8M6eNfupIXLpFIkV4i7h90HM0fT5vmWvr3ywseVHX1r0cXF0qNKk+q5vv/4YockT+X6mnQDI9/SjGABzipY49o4/OvNlsMSL5W6U7eDKKcq7j6VG+1GyTx3PpUAHR6dINqjtQCD3B4zQzbkHFACSLu4HemluM5/Cns2CPw68UpAPofelqAi9M0UoJHGMe9FAEk84F24/2yKjZsnNOuod11If9s/zprAiEkDJz0oAdAfOU47frUN7fpbAFjgkhRx6nH9akVjGg9/Svif/AIKh/t0eM/2Q/jV8N9O8PaML7SPFCtHdSSxzhRKZ44l2ujquQZFJBUn7vIzXdl2X1cdiI4agryd/wV/0M6lRQjzM+14pw2B3IzSCXZXxV+zb+2H8SP2hP2vm8L2umCLwdp+gQXeoaqVumihvms7aWS3BDGPIe4AwxVhzkZHKfBr/AIKKTeLf+Ch3xF+GN5AY9P0e8jsdOd7olXfzo4mIQtjO5/4RXf8A6vYxucYWbhHnduivbUz+sRtc+1/P5pr3CqMtnFfm38Uv26Piprf7Wuu/CvRbazstQ+23/wDZgOpXgku0he5KKqoA3zC2IAVW5bArU0f/AIKQeO9Q+GninwTN4cWz+JHhF/LmN1d3A88JcwIz8gTgFZTjK/w9ea7XwjjeSNTTVKVrrSL0Uty/bxtc/RAXqYDevHSnB/lr85vjF+3f4s0f9gH4V61p8lkPFvxhu5dOEkN3MRpiMZ4jMCriTKs8JJycEfSur0/4/wCtf8E/v2hNG+H3jXVofE1prdoNRj1COeSEBcThlZZZCM5RQOTUR4YxUrxjbnXNZd+TSTQe0srs9E/aW/4Kh+H/ANm79qm1+Gd3bS3eoXOnpeHyrJnMe5JJBlzKi42x9gTlh74+pYA6qQ/31HzV8A+Gvgfe/wDBQj4m+Kvi/wD8JDofh+w0zVLrw/osFzaNdbIrZliEjyeaoXdvmwE4+ZfU15/+358RvHXwZ/Y7+D03/CXywa9LrUthq8mm3lwD8xkZSW8xXIwmQH6+2K758P0K86ODoS5auimn/M1f00tYz9pNJzlt0P02u9cttPbZLLtLHgbSd35CoY/E1pPcNEkhMgGSNh4FfB/7bvw+1jUviv8AACODXtTXT9Yv59KvBIrkgtewqrth8c+eBgjkIOeeF/4JvWutaJ+2b8VdF1PWL3UbbwzfalYW0ZeT7P5ay2hjYIzEBgkmOOOuOK4FkMXhJYmNTWKbtbs+Ubqu+h916n4jt9NtvNnl8tM45Qnpn0HtXmX7Szprel6LatG8jy30OwKQCCLm3I6nHUV8Yf8ABbzR9X8B+OPhR4l0/wAS63ZQa3rz2M1jb3TxRqCLbBUKQOkbdc8ua+tP2j9RfQvEnhCRbmK1jhnknlad9pVVeJj3HYHrV0co9lTw+JTv7Tm07cu4c7lK3Y9c8C+IrN9JtdOSY/a7C1jjnjKH92Qid8YP3h0Pel13x7pmgzrFeXQhklJ2Dynbd27A1+b/AOxL+05qmnf8FS/Huk3uoXF7ofiK41Sa2jN47RBo2jRWQFtmNts3AB6nmuV/br0vwz8Jv2qfGqeIPEHiyKLW9GuL3TIlvIlWK+kvLvaFD4/dcAfL83A5r0lwZU+urDTb96Cmrb67r5EqupK672P0d+Pfi7Tm+H9xpU94bWfWQqQMY2IKrIhk5Ctg4JxkdTWro3i/S/hp8INJvLu5lFjaWVvH5qxl2fKqoOMd/oK/M34++D7zx1+w/wDCTxP4yuL+XWLXxBJAW85iWhk1myiO4yqW4UtjnGMV9t/EP4c6Z4v/AOCfOkaVJBFeaeNC0d4UnRJBhfs23+EjOO4FcOMymlQpwpyk3+8cX8tNC+d810egaD+154M8ReJV0e1ub430oXbutWCEFtnX6kVs6b8cfD/iTwjqWvWF7JPp2jxPLdP9ndWRUUu2AQCeAelflz+wonhn4r6n8NNEk8NvBqOj69BqB1iygiSS4eI2CCJ32MzQ7nZyuQckHPNVfiV4+1X9gf8Aam8a3+gaJa3nw28Q31pYanpkcbpCNmnWqyLtQLBl/to+8DnjI9fUnwdSljZ4GhL94tUnb3tVp5XWpE6zjHnZ97aj/wAFN/hhomgahq1zqGpWum2F6tg9zJp0jK8xMo2qq5frDJyVA49xW38F/wBunwH8dtbaw0O9vpLpV37ZLJ4hgsqg5PbLD3r8wvFelad8Rf2E/iz4rtfD9np1rf8Ai+x1LTka1UParLfakGVSFwMCTb8vavaP25fD9r8HPgT+zv8AFDwvYQaDrQtdPs7iKyiFqt2ht4bkGVowrMQ8eOT/ABHjNb/6rYPmWHkpKpKcoLVWTjFS/PQ1hPmipJnrn7YnxE/4a++KFh8M/Aniu00nxHpAlOoR3lpIkciSwxXEZRzBKMrHDKT06gc1mfs4/wDBQvw/8Dfh5428Da5cNeXvwQCWWsXsFjIwvJ5r4w5Q5QOA7nOI4+3BFaPwt0e1f/grn4g1DyI0u7zR9OkCpEBsIstQjJz1yVUfkPSvGPjx+zta/F/9or9rrw+mo6b4dN9P4avGu7tQsXmAI5V+n3t7EdyQPeudYbCJxwlS6hywlfs5Nc3ru7GMLv3rnlX/AAUW/wCCn+mftGaD4E0SJH+z22rLrMrx2JiLRhQm3LOeSJDgY7ckV9Wa5/wWe8K6JY3lhDHdyX8MDXdm401vKaNRlt2ZQc5EnbsK+Q/hrpWr/tIftzfDL4deO/Dv9nT+ANOiLG4t3L3UKahaW5+WZSfLzG+OMct719f/ALQGkQT/APBZv4cJJYQyWupeG2tpUMQMciNFqCspXGCCAc5yPavqcxwOWw9lg3Su4QnU0lppqunVbmqk+VakH/D5vSdPs/CslzazGTxPDcPDs044JiCk7v33AwTj8K1Pid/wUE8F/tI/sT+J9etDrsumWcsmj699ks0hmtHawmklMYmbDALuwRu5A4Nef/8ABbOzX4EeFvhNf+E7O30+7sdW1RbVbeLydnnRBpApj2kDluB+Oea+aPgN8btH+Bf/AATx+O2u6hPFc698Q7+XRo9MhlRJLeaTTLxxOVZt5BeQqeM/KOprjw/DeGxGV0s1oU7NytZPrz2/LqYxrJ1eQ7L9l3/gobceDL3Tfizcw6lLpPivVU8PJcS2luWCMY1YmNHBBBgfkZ4A4Oa+ufFf/BSq6m+Mlt4a0yy1O6s5vD0WtO0Vpbq0olisJY8GSVcDF02QQDkDHA58W+DX7N1n4z/4IKnTbh7a3vvDr6h4ghuJoVO2W3vZ5AuSMruTK5HPzehrvv8AgjV8JbUfCPW/Hd/rdteavr1nbaU6bgf7OhtbiaBV3MSwDrbxYGQPlAxwMYZzQwVSlVxcqetKbp276+6/uuVKTVXlXU4f9nr/AIKy/Ej40yadef2TBLpR1+20ieVbOCNI0kwSMGffv25OQCvHrX0L8H/26vGPjL9v6++D2saHbWNvY6adSllESbwn2eOQfOs7A/NIBgLn+dfn7+wbpMfgJPEfi6fxd4d0vR/AfjBLq6sJdQ8q/wBSjhzKTAhKqwZYWUZON20ZxXuXwm/a98I+JP8AgtNfeMHuBZ6DqnhU2UVzcSQxrFIsMf338wpyY2Aw2cleK0zLJsK6+Ip4ajdQpyat0l7r/UFOTScj9N/FMt6/hq4/s5Ipb35PLSThT8wznkds96/Lr4P/APBX7xdrPgz4teH/ABv/AGPZeJdN025XRVs9OYos6wXe5JGDspw8UY9OTye36FfAz9qbw7+0P4o8VaZ4f/ep4UkhimuRPFLHceYZACuxjxmNup5r82f+Cln7I3h7w/8A8FIPh4sFxcDSvHt+t3ra20Mfm2JfUHZ2XAC4YSEfP2Q5J7fM8J4bBzr1cFmEWm1zJ9U4+9b5lzu2pRPof4u/tseJP2a/+CeXg/xVNHa2PirUdbS0a3e2E8awteXO84VyufKhbHzHntXU/tV/tleN/DP/AATL8O/F3wHPpZ1maHTLm+N5a5Qxz4ilCxk4z5zpjnoDye/kX/BV/wAK6l+0x8Yr74YaLYIkXhXw5/wkj3M8bGJmijuGKqEVsnE4wMDJH3h1rwHwX8XtUuP+CY/xG+F+qeGtaI8H3WnW9rerZu9rcH+1ZmfarEbcYxx3zmvcwmT4OvgqGLVvaOrFyj/07m7JfIn33Pl6WG+Gv28vi/bx2XhaTVtGksPH2iTXYxYR7oWe1kKlm2jHITgBuh/H7a/4InfHvxJ+0B+ylc6l4svYbzV7PW7u0MkVukP7sLbuoIQBc/vDyB6V5b+zB+xf4V+IP7N+l/Ei+0vVk1vwd4aktoNLk0yEJq0g00HzGUqXl3NLwRgkr71p/wDBBuTW/CHwp1zwvqXhbWNJt0v7q+ivLmykgilJWzXYNygE/e6f3T6VrxFiMtxWX11hKajKEo30Sv8AFt8rFU4SjZM/QczeWaKjjAx0x+FFflW5uXbg/wCkSf7xqPbubJpk6FLifqcux+nNOjfcmelIBV4z6CvgT/gvToFnrXwu8GtNM0N5HdskHXbh7zT1Yng9q+9WUyBsNjB6+teefGT9mP4fftD6hpl1458IaH4qbRA4sxqMAm8kOVLBc9ASi5/3RXq5LmCwOOpYxq/I727mdWHPBw7n5+/sPftmX3/BOW90vwJ8VmtLb4c+JbMeJNF1ewtWu5gbuCOSNX2EOOYp1I8k4OOcYNeQfHH4Mah8EvC/gj9pjT/E0N2vi7xNJrIimXcYv38l0AIhbrj/AFOCC7dhnkmv1uuv2dPAuueCLLw1f+C/DN94c0tUXT9MuNOimt7ONchFRWUgAbmxj+8fWuD+HGnfDT48aZqngxvhha2+heAL2S1t7HVNHhFmGEs0Re3TkYPluc4HEg9a+ow/GEYYieNpwalU0qWaSlHXT1bav00M3h4uHJI+Efif8fPDOl/8Fifh74uu76KPw7Pb/bDcrbzl40abUG3FMbs4dOAD34rpdE0nTfib+298WvjfBdeX8HoUfSJdQIZZ57sPYodsO0y7TKw5KjgHoMZ/QmT4BeArqdd/gzwdOrxiMbtItnBQZwuSnI5PHv71qyeDNC0Pw+NJTTtCsNBQAfYPskUdmpzkfu9uzO4A9OtcdTiqPuqhC0lTVPV7rmv9/Qp0U48rZ+OqfD+f44/8E8Ph5qng+T+0J/hNf3t3f27sITBBJcXcyuvmBRJxa9A2eRxycey/HTxBZ/8ABUr9on4aN8OoJNSt9Fs7iHXbm5/0Fbbe8rxoA7bmykLnKKeWGT6fpBoVvoGkWZGj/wDCPwWKDE32ARRwxoM/f2ADaPm68dfeofDPizwdounuLHXPB1pDIS7C0u7eFXx1YhcA4557YrarxjiJVfb06VpQc3Hy9pq/Wz1QQpKPu3Pzg+Ev7Qekfse+HfiX8JfFdzeaP5Ov3MlvNaW4usSGa2YDf83BSOQ8p6cg1yvxr+HWq+MP+CV3hDxFqOZfJ1htSgYOi5jRdSOSoHoE461+m/i/wt8PdRnj8VavbeELlQBHFq1yYGjbO4ACVvlb7zDr6+lY2qfHz4TaFJd+G7zxJ4FsvsO60uNKmv7ONYzyGjMJcY6kEFR16c1suK3Kqq9Kh+85lKXVNpW0XS99dy5U7po+OLb9r/T/ANq34x/Arwv4et73/iXa1NqGsPcQJCqJBcQ3i7DvJJ2Wz8AdcDvmofgb+0loPwZ/b4+NOqXi6lPo1xqd+gjghVpRKJbSNidzLxuibv0Ir7n8L/Czwb4Q/wBN0Hw5oOm5jKme0tI0O0b+AwHA+d84P8TZ6mvJ/GXxz/Z68N+I9Ut9Zb4frqVtdvHqHnf2cJDPn5/MLSBt2eu7nIrGjm2HqzqQo4eThKLVlLZuV29vkYxotL3nqfDP/BSz4+yftA/BL4A+MZYZjHqniW+1WyEsSRYskuVCqVVjhvL8ngnPB5zXQ/t7ftvat8T/AIqaBZ6Hp81lpek+HtRudVS4giEzebFOEKkSuMAQE8EHr1yBX3P4c8cfCv4pfD2fVtNsPC+q6B4atZXKm2s5orCBd28KAWRFPknuoOwenHgHxn/aQ+F3ww+PHw/uI7fw5pGi3lnLeTGKy0+NbiNZJozyWAPMbL1wM+ua78DmsKnJRWHd6XPbX+bW23S1iZU5XbvufJ3xh8OaF+zp4D+EvxU0ZL+TWtY0qO9u1vGEij7V9vD7EXaAu7BGWyMn6V337V/wuuf22f2u7mNrCB57bwkUt/3xt1W9N7MF/iPGZO/Ffo38IfHPg34//Diz1zw9baVqOiuzxREwW8yIUYgqAhdBjPQHv7143+3P8UdU+EHjj4RLpOr3Og2WseJksr9LS0ib+0UMkGImLEYBBfoc808NxbjJYqCp07Vaakk762etvlqrAsOlv1Pz/wDGHxL8deJf2XPDHg3xDbWa3VtrshtERUEwAurG5csysY8AYI79RzxX6R6S9zcf8E7/AA4kqs92NB0yFli2gtsaBe/HRef0rz+x/bs8M/Eqey+JNoNa0jw54TBi1GxuxClxcu5KL0l2jll6sODXTfE3/gqf4P8Ahprdhp9n4X8UeJL7UdItNdWPTvJdore5RXQEBydwV0J4xhuCeM8eZ47G4zkpqgk1J1NO73Kp0lFnxb8HY/jX8LvgPa+APC+iWNlJquqrBJLPLaySrDLbpbuwYylMfJGfulsjpjIr6R+DHwP8SftG/Db42eE/HmmW0R8UXEEunyx3Kx75vsECRvmJm2hZraLIZei9CCa+wfhv8QrT4oeCNN8QaTdPJp+sWsV1CDKGIWSNZACVYjO116E143+1l+33p/7L3xE0Lwzc+HNS8Q6rrVhNqCfZ7hUSCOPccHILZIR/4ccfXHLUzjG5hiXGhRiqr1ulrdNO97+Q/ZpKzPkHXf8Agnr8XPCv7Gfi74caJpdld6reeILY2qf2hb+XJaQXV9IHLuVxlXhOODlugwcd/d/si/Fz9oNPhr4b8Vpb2vgrwE1pPeo1zapKrxeVGY42iDM37pZevcD5s19EH9unQ5/2VZ/ig+lX9raWZjSexnmjV0dro220OTjhlJ5AyAOAenOat+3hbJ+xk3xXtrIf8ehuDZG8jYpJ9hN0Yy+0qGHC42++O1brM83nd8i5nNq9tedpJ9ewKMY2OG/bD/ZV+I2r/tYaT8VPhrFBcyyacllq8EtzArlohKkTRrMAv3J2z8/8PTpngNY/4JsfEHxh+z58VDJNZL8TPivf6fd3UNxeRi3hitLuV0QmOMoreS0edpbJU8+vr3gv/golpvxKufhJJpOmXD2nxL1G+01z9oic6dJbyRp8+0HO7zFOAVOD34r6A8V+J7HwTpc+o6pcRWllaMBLNJIsarlgoyzEAZJA5PeuSrmeY0IQw9SKvCyV1q+WWkb9k/yE4a36H54/8E9tA8UeL/8Agp94t/4SuWVrn4e+Cl0QJJ5CmN01Y5VfJGHQGBuWO765r3H4r/sQ+NviD/wUF0D4rxjS00DRjbRMGutszxRxtuITacne56kcD8/Ef+CXHx78LN+2n8dNT1TWLMXPijUWTSJZ7iFTJb/brliVJflMzRHK5HTnpn7d+E37WXgL45eKLrR/DOv2Go6hbozmGO7tpDIqhCWURysxA3jJx2PpXoZ3isbhsZKUI29xRemlnFXt26m9SKbsuh5R+3p+xV4q/ap8Q+CZtHj8Oz6f4aluJp4tTu5oDKZLdIlx5QycEMeo6L15FfF/x1/4JUWfxP8A28JvA3hbUNKitk02TxVdWlze3Kva7tQaBcSGEgqBuG3cx4zk9a94/wCCp3xn+OP7MmoX3jPw745u9J8CWlxBbDT4LCIktLFEB+9eM9JRIcbv4sdsV47+wD4z+IXwF+NHin4ifEbV7zxdqvjP4c3PiaBms1t54oEnhuI4mJQA/NPLyBjJPXt6uRVczoZf9aoV1yxTUI63bum/LS9zCajfVan198Lf2Ete8D/sA+I/g/fahpE2r60t1HHeRXEht1WZ1Ybm8oMCMHpGR0681ufsZfsW+If2ZvgbqHhK91PSLlpkiFrNbTSSbNtxLK+8tEn/AD0AGFPT8a8Q/Y88G/tN/FLxL4R+L+r/ABRuLvw7qmpfY9T8FzwOiR2aO0Eko2w7c7k8zPlp1xvHU/f1rbEyL8rZYfMO2a+RzHGYyDnQlVUueXNK1/i/4BpGK0kkfBXhX/gi9deFtC1jSx4sgNlr0nmXkn2smdvldSq/6GFAw7ds574r1fWf+CXVg/xok8d6H4j1nS9Za1NnzcQPEIjH5bja1s/JB6561lf8EzfFvir4l6f8cbHxL4n1HVpbDxheafYyXFy8kmnR4dQsYJBUDjABHI7V82eLvgDr/hn/AIKL3/wnf4nePdQsLbwbL4tS4OsagpeeJW2wn/Sy4/1YOd5HT5DXq0cRmNXE1qNXFcslG70bumldfdYHpZI++P2Xv2R9P/ZwbxHdwXd5qWq+KZY5tRup5lYSsjzMu1VjjC/60jhew+p1vHv7MvhH4lfFzw1471RNSPiLwiSNLeK42Qx8liXTHzZJ7+lfl5beDfiFa/Cz4k/EDT/ib4xsL7wPrqWFtE2p3lx5kT3tzZMG3zbc/u0OWVj7g5J/V/4JeOG+I/wc8Ma+8Txvq+k2t5IjtuJaSBJDzgZ+96V5GcYCrhJe3jW5m202rrWy/RmidkVrj4WeEvDvxVfx7NBJF4mv7VdLa6MsrI8RIwnlglQfkHOO3WuZ8d/CP4aeGdI8Rza3btBY+OZY5tSzNct9qdJRKhGwkp87Z4x6dOK+IP8Agpto+q+BP2urvxj438J+LfE/w0k0y2gsb3S2uimgXew7LgY8uLMUiSPjzl/1nPWq/wDwUn+GfhH4m/8ABLLwD8QdHWa81W2ewjstYvXZrqOCRDFJHIBLIgP7qNDlmwYxzmurC5KpSw6dWVqrSutbPdLfdCvK9z7S0n403Fh8WPAPhPwRp9pe+Ans2try9kVxNZGGE+UieZIrnhY8ko+d3XOce5faGnTcTk59K/OLxJ8AvC/wD/4KCfstW/grTLPw1pOo6ZJcXUFmGUX1w1uVMjc8kjZ3P+P6MtEypsOVPuOlePmeDhR9nOEm1JX19Wv0KHu21QfWim7NqetFeXbuBamwbiT/AHjTURVbHamXCsLuTkfeP86jYP5o+brQBM0CH/8AXUF/uhspjbrvnWNjEn958HA/PFIZGYnkjBqjr9ldat4e1K1srtrG9mtpYre6xn7NKyMEkA77WwfwoduoPY/ND4jfEm90L9pXxZqOqeONQ8AfF638R3sFpH4j0tbXw82igOtvtn+yOrO0WxlJlyxB57HR8feMfir8UX+P2j+FHl1mfSNajN5DZWtvLIdOeLUt4h+U7yR5QHVs49TVP9oH4XfFv4j2Pi34T658NovG/iu58QT32mfEu40+VQun+abiC38xLJn+SI+RxKw7ZxxXVeGP2Lfjh4Z8X/FqXw9rr+G7m4urG6trxftSDxAkEFyHiz5PzBndOBvHPI6A/oMKuHp0lUm4c1lZPVaOO1tUt9HroZJy2PR/+CXeveFdM1PxPo3gzxFePoEstvLHpGt2z22rQS7J9x2tDHuXYkQOGYAxSdO/W/8ABYK2muv2CvFKW8Rnb7ZYFlXqB9qi56jvivM/gb8Lvirq3i7xV8SrfwTpXw71Wy037PpWhrbSQf2hcGO8Ikb/AEKMHDXEak+VIfk+gr2H9pf4O+Ov2mf2CpfDE7WNh461a3sZbvc8nkJOlxFJKMpCr9Fb/lkvPYV4deVKlmlPERacU4t9df1RdS7i0j89vh98P9CtfCfin/hSFv4xmsL74f3h8YT61YNHaBjBBjyZZI1BJZrwjYTkLnsK9C/4J7/s3fBf4iaD4SivPhH8VZ9Z1QX1tJ4meC5j0uHebiMlpFnCACPamfLPzepr7r0z9mSw8P8A7LM/hHSdL8PaVrd94UOjXVxaWCQLdXBtDFudkQOy7yx5GeTxmvGf2Tf2Yf2g/gjpPh/RL/xb4Nj8L6beiW4tbeDExgacySopazVstluS4xu4Ir1q+eUsThKkU+Vpq1202td7LUy9kou54/o/wY1rXf2pJ/2ZrqzQfDnw3qd34wtXkk2zPZywy+Svnr8xxNdqMFQflOWOOYP2vP2LfBH7Sf7V8/hb4cWN1eeJJ9a/tHx3dLdytDplu7RKyq3zKjt9oc42k5hbGNpB+s9M/ZP1nSv2/wC8+MkviGzl0S78NLoQ0dUfz/MHl5kJ+7tyhPryK8C1b/gmL8eNB+MPi7xZ4G+PGjeE7nxdfzXV1KtiZbqWFpWeKJywP3A2OD2HoMRQzan7RVKdVU5RppdUnJ/E3ZPXr56Fq9rM+4dA8MW3hDw7DptnHItpbhggkJJG5ix5+rGviv4ofBzwtP8A8FYvC9nc6Jusdc8PzXt4ftFwPtFwRektu3jH+rBwuBx06173+zh8F/if8KNc1+48e/FI/EC01UW/2CD7ELcaeI1kEvQ4y5ZD/wBsx68UviN+y9eeNP2tPCnxNh8RR2UPhvT3sX04W5Z7zcl2oO/cAAPtKnG0/wCq9+PDy/EKhWqOU7qUZK6vq3/wRNux89fsv3ljZfC39p/SLTbYnSBq9vGhkCtGizaoqcSEngAcsOeDzmvl7XvEfiDxrq3wmGkeGv8AhKtTufBurCexUjzjGLvV+VVJkydokbAJJ2dD0P2H8bf+CU2r+P8A4p+KfEPhD4sar4D0zxxO0uu6PaWs5ivEdcSIWW6UHcWmY4VeZTWlpP7K3h7wH+3X4GutEki02x8LaFJaR6akJZJ1mGouxLGQ8ZuHOCrd/Xj6jCZzhYTniKesmm7NPpG35si0mty3/wAEjtO/4Rj9nPU73VrnT9MnvfEd+smnPOI5NLkTyojbyK5ysi+SSQWY4YHJB4yf+Cwl8dC0z4PajbxyPNZ+M4tgRd5wQrcL3OUFd14m/YBtdU1fX59L8Z6/4bsPEGuya/LY6dLdW8cdxJEI5Npjuk4YgucBVyx+XPNen/tC/s4aD+0HY+HYdcXK+G9Uj1a2++cyICMfK6dc98j2rwo5vRWZ/wBoy1TbukttP+CV7zVj8f8A4T+JvEngD4KeL3aO6m8MfEWSK0nnW1Df2dd2uBEJGCgRh3mt+u7IJ6V9CeLfhjp+t3XhPW/B3xA0Pwr8RLLwLokOsW3iO5W2sriL7Jbr5kReBgSVa3xtcfck44NfWnwl/Yi+HL/DzxX4NbRbe/8AD9zqUU7RySzM0EojgfKP5hdDujjPyuM4Fch+3T/wT4sfif8ACbT9P8CeH0tfFVnFZ6ZBqsd3eRvHZ26sBFIYt7OAioMvuOdmTwDX0+N4rw1fGRcL07vV2ummktV8rP0REKcopne/sSftM6B4o/Z/8HQ6tquh6Xqd8sGl2Fv52walIltag+TuZi+WmQZB/jX1ryD/AIKp+H/hhr3xM8O/8JB4lvvCHxHttEuG0DUJ2EWkzRZctHI7xSJv4kXGAczR88gj6Q8Kfsk+BPD+keDUTwtp0M/gmKN9O+zeYiWk4EGZAARuObaHlwT8g98u/aE/ZG8DftP3WizeMNE03VTo7nYZ4T5hjMkbtGsisrKG2Y4P8R98/HYTH0aGYfW4uSV3tb5fLujTeOp+Yfxd/aU174p/sQad8MGt/wDhJb7TfEgg0+XTrT93rFtC2oM8kT5Xzdm2DcUUAEnjBq/8IdG8SeHv2JfjZ4B8U6VL4d1ubSpvGlhbXgWJnsZbC7g8z7xPDxqCpGRX6Y6F+yV8K/B9vpEeleA/DFsnh4Spp2LRZWtfNyJTlslmbJyWJPJ55NbGv/BXwX4nu7u61Lwtod5cXumnRriWW1Q+fYksTbNxgx5djt6fMfWvoanGMPq7w2Ho2XPz3e99Pl0I9m9rn5g/B7wFc/svftF/BHSbC0uH+H3irVJtXtJxG88kF1HKIrhC2ARnyLYgEH7/AARnA/Rjw/8AFPwj+0V4X163sZbu7sNOvZLC+jmt5LZ0mgupIXA3BSQJrdxkcEAHoRnYvPhD4VuTo5fw1oMh0Fnk0pms4ydPd2DOYvl+QswBOOuKgfwro3hPS9Qj0Ww0zT2u5WuLoWUSRb5nlMju4UDLNI8jEnklmPc142PzR46pGpKPvrr31vd+ZSjryo/H/wD4JHfsz6n8bPEXxwv0069kttE0i9sNHbPl+bdO26GPOMMxEY4z3969Y/4JS6b4s1D9qDwdpmrWuvWkfhi1vbiS0udIktlsQyzYEkjRAHcbjcBvJ/er6YHs/wDwQO1fTtS+AXjlbVbIajH4m/0kwsvnuv2aLDOByBu34zxnd717d+138dfA37KXwD+IXjXRLbw0nirTLD7LEmli0i1CS6n8qKBSQN33pIGwQSQFwp4r7PPeIsVUx9fAOmnzqMVpt7tv1NOVRdrnzD/wXQ+Kc37TnhK1+CXgGz1Pxbq+j6qupeKbTSLJrqWxjiiXyclMlf3k6gjb/CR2Ne2/HP4Jal47/aV8N6Va6JqieHtT+Ed14cS8ET+TZTSXVsqxSychHCMTznhWODinf8Esf2b3s/Al18Y/FSDVPGfxjtl1e6N5bM09nA80s0cRLnB/dPAPlRB+6HUYr6n8VeJ9M8H+HLvWNSaC2stKt5LmeaXYnlRopdvmYgAAKTyQOPavk62Z/VeTBYeKtT5lfXVvd/LoKfvK1z4n/Zs+IH7QXwy8PfD/AODj/DrVNN1jT9diudb8SNp8cmhppD3L3E6pdecy+btcJgR7s5A/vV9b/CT4t+I/Gnxa8a+HNW8Jaxoul+Fjapp+sXNoI7XXTIjGRoH81t4VgP4ExuHBrz74W/8ABRr4a/GHx/pnhnRJ9Tl1HWH8u2lYWpicgE43JOzfwnoDX0GIXto1dtwXAHTrXk5lXnObdSmoN6+rb3M1HU/Pf4HeGvj9+xj8WPi1B4Y+E994k0rxp4oudbtrvbDLE0bTTBTuN1CRlShxg8GvQLj9mX4g+K/+CoVt8ULzw/8AY/D994EudFvLoTx7YblhOiIF3seR5RzyPmP0H1t408eR+CdNnuZvMdLS1lvJI0cbjHEAWAB+v0rC+APx30j9o74V6X4u0QSxadqzTCKKWRGdTFK8TZ2MV6oT16V0TzbEO+JjBe8uVvXX8d9C+Vp3Z+eNx+wv+0s/j74peDNK0LQNO+H3j3XJdRk1e6vYC80cd3NdwbSGZlJeXkeV7cYzX3J4D0j4meA/ipoXh21t9E/4VNo+iwWZnZw1+Zo0uEHOckYSz5293/Dp4/jtY3Hx7j+HgtLp9RNhPqH2gOpiVYvs2VxnOT9pXHH8JrB1/wDamsNF8feK/Dr6TffafC+lDVcCRVOojN5mONeuf9DPPP8ArB6crHZjjMakpwVkk9Fbsr+uiNIx00PmD/gpH8PvjN8OfH2reKvhteWN34Y8aWUHhzUdPnjinuS1wvkP5aeXvHCRchzjLHGOnY61+wRqXxi/4Jl+FPh0ZksPEkq2ur3ZuZzEkc7ySTyoT5bEYM7jbt4IAzxmvW/hT+0rpHxrnu7fxJ4F1HwdFpEbagH8TRqsaiIoRKvmqAMbyQ3by254r0Cy+Nngm70C6v7TxZ4Yl07SyqXM0Gp25htdzFF3kPtQFhgZIyeBTebYqnRp04wUXTd7pavtdrsG+h4/8c/2NtX+I/xZ+FHirSNQs7K6+HenS2cjzzEGV2iCIyr5TK2GyedvXp2ru/2Nvh/43+F3wMs9G+IerWGt+JobmeWW5swgi8tnyijbHGOB/s/iaZ4j/a08HX/wr8b614X8SeHtcu/CFnNJJHBqlu4Eyo5jVmRn2hmQgEr2PynGKb8EPjhqfi7XINJ8UQaXo2u3VrJewacl+HuZYVfYH8poYm25V/mAI+Xr1xyVvrMqNq20e+662X33A9bAzRQrZx16UV5vqBNcxB7l/wDeNM8pVbOelLdv/pTjuWP86iEoCkHrSAlUcHHfrXM/Fr4laR8F/hxqnifXLhLXSdGiWW4lckAAsqDoCeWYDgHrXSQ8RivEf+Ck2hf2/wDsDfFiLGTDoUlyDuK7fKIlzx3GzP4VtQgp1Yxk7JtX+Ynsanxd/a58O/Bz9nHT/ifMVvNA1VLSW1xI4EouFDJyI2boc8oOnOK9CsfGmi6s4jj1jSpJxgtCt7G0iH0K5yD9RX57/tXeIbC6/wCCG3w7L6gwki07Q9haORjK6gRsvTthuTx8vuKq+DfAo+PH7Td0PB/jHxh4X0zwdqFvd+JNRm1rUHh1aVnRmtIbcTkqoaO6UnaifIuAQwx7tLJKU6Tq3cbOava6srW++4c1kfov/bOnKBM1/Y+WZBEshuU2mQkAJnONxLKMdcsPUVm3nxT8I2PiRdJuPFfhy31iUHbYPqcC3DAZJIjLbuArdv4T6V+eHwp/aNkt/gJ4wtNR8Y6tqOu6Z8UIILRJZLgv5S6hpoMavgqE4f5ScYJ4554v46iGX9nr4r/FBtR12DxhofjRbWx1FdTuVksLeWOzBijCybQuLmTjb/y0atqPDjdTkqzt0Xq7W36alNNK5+m918c/BWneLn8OzeL/AAxB4gRhGdMk1WBbsO23CmItuyd64GM/MPWvk34jf8FY7/4X+JNB0nW9M8BWmoandzLcsutxTR2FskcDoz7JGCvIXlVQzA/KpCtkA+L+Bvil8I7C+8S+IPij/bcvxT07xKk1w1lcXsl0HM15JBEsqSRxbDFHbjqFGxMr8pxwOl+APC3jT48+GLXXdGtNVk1nXNRtZvtqeYdsemWLxKfvD5XcsMHq1d+C4fw0akni23CK/wDAnb7L6pMVro+6/h3+39D8UvEHgeDTbDSLi28WTXVtPcW12ZRavAt8w24HO5bRGx2E3fGTB8Hf27/7W+JnirSfHNx4T0TQ9A0u1vrXVoLnAv3khSWRQPMfONxwFJJ2968G+Dp8PeDPEfw2tdIgtrNdL8Y69prrb25Ty5EXW8L0GcRBBnngAZ4rwrwF4M8TfEb4oTX9tZibS/AWmRazqdhcXKFNes7dIC8ZByuSilArgjEp7ZqFkmDm5tS5YpXV992l+H5kydkfp3+098V5/hp+zh4k8V6KYXvNOtlNqZ0cIXaVY+QCrD73HI5rwj4GftT+NdV+I3hXS9bvfCuu2PiuxW8aKwuc3mmM9o1xteP7TMwCtGVO5E/1g6HAbq/2sfiXpXxs/wCCc3j3xF4YEz6XPpE08AdPs7r5E/zsF7EGNiPXA9a+M/2ZtT0H4o3PgX/hT48Tf8LStbNINavdTuWWzTZZuLgL51xIv3jEF2QjrxtG6scqwWGlg5e20fM1+Ctfsik1bU++tA/bS+H2v+KptBt9baK6eRrSwubmwuobXUrgOIvLhmeJYpTvOAEkbPJHAzXyV+zR/wAFBVufHWnyeKIpdZ124ikhgazhuri4dFSck7FSaQBQ+ck4IU46HHnvwC8Gx6v8T/DHg3V5vGOp+NfC/iGO4vbEGKOy0gi8/wBak4vR5qrvjyBHls52kjFcv+z54E1/9mn9quDxNqvhufxNpv2d7aG0hntVkt3e0niB2ySbAHe4T7pJxGSR0z7uXZPgIwxMHLmko3Wtr2etvXcl2R9sQf8ABQ7RfAfwjGq6pHJqniHUtcvYdP0NGnF69otzcIkjL5TyIFWFshkXBXGF4FS/FD/gqX4I8JfDjw9q2jQjxRquvXZsv7Ht5ZkntZhEjujHyGOVaWNMFV5b2IHzB8Q/2R/FXiy+0/4savpup2Hhp768WTR9O1VFv7SOe5vJIiuyeKLGZo922QH5mGCM5s+OP2e7TRP2eE1m2+EusRWa6xcXdpcR+KFXVIC1tG8d0W+08BgmSgmJDxrweGHF/ZWUuUPebbk72at6b9Abse+/CH42aN4/+Nfwfv8A+19fs7vxINVa009Wngtrzyo5I28+N4gWK7CVLFMcYzjnJ/4Ku/tSat4MvdH8D+FtRi0/Xi0GrTSR37WsywlbqMqSGQYyEP3vTiuU/Zc/Zg+K/hrx7+z7rHiHTrR4fC9zrv8Aar/boGksoZgywj5f9YSxc/LnAYAkdB7J8Rf2AdN/ac+PfivxV490vFmVj0zRXh1GdZWt40gZZMQyx7MubgbSc85ycivPovAYXMfaV5c9OKe2t3ey/AXS6Od+O37VGv6/N+zrrvhKP7Zb+LdQg/tGGG9eGAtJ9gfy2yV3cSEANnhj71Z8Y/8ABRnxp4P/AGhbPwnqfw/0bTPDuo6ja6Zb3N1qypqdx5ywhpUtziUqsk4X/VkHy2+bgleIm/Yb+Lvg208N2Ompp2r6T4F8eR63ocR1QQM+koEVIMsCVKrbQjDFs+Z32knxvxz+zh49T9unwf4Z8S+K9P1Px0NVtNWtLy61G8nM9mghcxqpiMUZAtrjHIyXBOOK6aGCyurLl51yRUn573X5omSlbQ9j/Zb/AGpdbvv2rfGXw+0GKDUNV1TxDqd3qK3kkh/sKzhnvHSRULIG8x5rZeGGA/Q9uZ8Of8FpNc8Q/HmLSl8N+GpPCd3r8ehQvBPM900UlwVFzwT/AMssceWOSOR92u38Jf8ABN/4m/Db4teJviF4f1fw1b+MNS1f7TbTG5kj+0WciXSzwTN5Tj70lq4BRwTAMbSAayPA3/BKzxr8P9bW2tL34XnS4fF39vpqTaNFJqEdkGULZqHtSwIVdwbzvvH/AIFSqV8l9rUlJc3uxtq0k7e9/wAAiKlfU6HW/wBs/wCJ8XxGv7xNC0ODwf4d1/TtBvRtl8+b7YLMGUHzhyhvAQBE33ByM5Ef/BPTU9d1L9oP49DVJBPpsutx3dmWDcLNcXsoHLtjAYDoOnbpXaWv7FXiGz8NePbG88R2F5P4r8S6TrunM0T4sY7MaeJIyT/E5s3II4G9fern7Ov7MXiP4GfHTx9r95r9lfeHfF8FkbbT44mWWzuII9sjsxHId3lPDfxDj05PrODVCpCla7ttfpy9/matI/Of/gkp8abb9lP9t74w6Jq7ppunNf3dizXTNEnmpfhEBIG0EqsvJ4+U84Br548K3Wr/ALVv7Rfiq9g1SSy0jQdIi8RXN8twXjWa3ktIkzudeheI5GSNo6YyPcP+Ct/wHl/Zp/avjm0W8jhn+NiTS6f9jQwG1vzeTHMhzg83kPzDH3DxXQeGf2BdJ+DnxKk+Bnh/xlFJ8V/Hnh99K1RbbTp0trGGW5+1Ndm4kkAYJbW8P7uMBicAc5NfqdLNcFCgs0v+8rwS2vyqGkm/63NPZSjHma3Oh+BHxb+LvxF+LFv8GPhV8Sb3xHJf6Hb6jq2szXN1/wAU0kFvbyrDDm8iQhpJzCdsnSIcYBx7d+zF+2td/tI/sJ/GbQfiBeafY+JfA1ld6WZLy4khlvf+JfLHvP2hiSxkikztY8n8T6f8B/8AgldpPwA0LRH0DX20fxhb+Hv7G1jXbGGdLjVZi9rI07P5+7GbeRQufuzYGANp5X4nf8EdtM+KPipZbbxzf+GtEutLFnrmn6TZTWf9u3O9y11M8F3EWZkkkUht33s5NfAYnNstq15KGiTTT5VzXT1fo0TeOzPLP2B/+Coum67f6H4J1/4nfDLTNLmsL8O0Tut7BIxmZAspu2TOWDD5M9B15rC8J/tBeFvhl+3pY6j4b+IHiHxA0mraudV1LV9eMWlXEckM7xxxo8aDarFVX99IP3IwORj2P4+f8ENPhZc/syv4f+EXhPwz4Q+JFhOt3pfiac3BldxKzNDK5eRwjoxjyd4HB28DHlP7Nv8Awbu6sNVl1b4w/EkarNJESmlaDJfwx2cxJBcXEVxbM3y4/g6sw9z108bkM/b4urKalK6UUl166dPK4l7K2jJPhf4I+H3xA/bt+Ktz4V+IV3JoHg3wtdTebPq8MsesalJqEx8mP5YwybLVD8okyJh8/TPMf8Ep/HMq/tHfs9W1q9w2mX+havbsqSMsO/7RrTklcYJwn8vSvfP2Bv8AgiPZ/sp/E/x3q/jrxWvjrTdZkU6JbW819YyWEKyyPi4ZZv35KlAd5kyQ2ScnP1X8P/2TfhL8FJ/D974c8GaLoc/h8SW+jzxI7PZiVpmkVCSTljNPye0hGcYFeVjs9wqpzwtG9RNRSbSVrRaf4smcE3eL0PBv2t/2ZZP2g/27PDWl2vjLxJ4Fa40rUriXUtDmMF1IscWnAR7gQdpJBOc/drwjxz+ztrf7NurfGDw5b+IvEnjqO68GnU31XU98t5GUXVf3SvuPB8nJ9fMbjmv0qu/COjyeKbfX5dOtH1a3geKG/Zf3scUnlh1B64bZHn/cFcv4V8RfDj4x6rq6WFvo2t3Zj/s7UjJpbK8sREv7l2kjG5fnm4yR87f3ufNwmeVqdJJRvGKSasukr7lXfQ/NH47fGrwt+098e7q6sdenuPD918OLvT72W1WW6+yulzcSgnCcgHyiw28Kx5HUct8GdO1rxh+zr8YfBOh+GbHW9ItdN0l7TXtL0p0ur0JqMBWKb5m3ttZ+PlINu3AwQv6jeF/2W/gn4J1eXSNI+HXgrT7y4tJElgj0dN8lvJ8silynKtkgjd36VyfiH45/s8fsi+LJfB0llonhK91IkXFnZeHpHjuCoE43tHEQ2PN3DOcFj0xXrx4ihKj9Xw9GUn7rXW1nvpr5dhxslofKP7a/7Ld1oTeEl8HeCpoLGX4ZypeyadpHlp58VndMPOKKB5hyBhvmyeOTitP9kT4rah+0D/wUE+HWv2Gga4ul6R4ZvLK71Ca2uFhRt9621pJIkH/LePAz1Ir7c8MftCfD34mpodnY3FvqH/CTxvFpsc2muFuIxErunzphV8txw2Ad2PaqHjO68Ofs76/4IsdC8LaBpS+KfEEWitJY2UVqYBLDcSk/JGS2TAoxlfvZzxzwrP6k6EsLVpXk1JJu/W6b8/8AgDPWRLk9qKhkfDEKeQevrRXyvs2wLVwm67kP+0ePxqKaL5OetOubjZfuP9o/zNNdi57VADos7ai1PTbfWdOuLS7iiuLS5ieGeKVQySowIZWB4IIJGDxTrafzcj+7Xi3/AAUS8Vat4J/Y08f6pomrX+ialaacrQXtlL5dxblpo1LI3Y4J/OtqNJ1akacd27CexieH/wDgmf8ACbRPjbfeM0sjqF3cmaT+x7mKyl021aU5Zkh8jK8sxB3dXPXNS+J/+CZXwh8Ya7/ad54fgW6a+fUZDHZWWJpncyNvzASRuJ7556184+N7Dxh+zr+wd4U+OXhz4mfEHUfFU2l6bcajDr2tyahp12LsKjk27KVyGkQrgrt2D3z2vxz/AG7PjT8NfEOr67p/gvw4fhtpTWzi9ugrXdxE9v50jIi3gOR5c2Nyr/Bwea9hUMZzKNCrd6re2q6E3WiPf7X9l34V6d8QbnW00Hwp/b15OJGd7Oz81Zw7tvX5A+/fITnOcgd6660+GvhW/tNQ0s6ZoN7a3E/m31o1tDIkkwCHdImCN+BHywzgL7V+f/iH4/8Ajf4l/tB3/wAXPB1lqEfw9+HGsjRtYtbvUpI4ry6a6dPN+yi6KyY+0QnOFHyj5flxXo/hj42fFy/b4h6z4JGg3mqX2r21zHHqbSG20+GbT9OlYbS4wAXwAu7Bk+rDTE5RilFSnUu7d9nfZ+a0foPU9R8c/slX3xA/a/03xXPo2g2Gg+H1WWG7Wygkn1Rw1kdkn7wONvkOqsUwB+GfeP8AhCNF+0rcnS9M+0RuZElFqm9HIClgcZBKqoJ9FA7V8DeL/wDgpl8T9M+C8y2Vz4WufGll4mg0KW7i05/sVws/28oUEhByPs8XLIv8XBzXoGteOP2odX8fav4S8M6t4Hu9Z8F2Ftcao1xAqjUp7kzyxohMYXAhjjXpHhieT94LEZdjZwgq8lFRTS1t21/ELn2BpPhDSNLdprXTNOgeSdrh3htkQmZhhpCQPvkEgt1Oabqk+keEdPmu7j+zNMtokJmmfZAkaAEncxwAoAJOfT2r87/j5+258aP2f/ED23izxz4X0TxNaw2sieGrDTWnSQSQJvaR/IeMneZm+WcfdTj+E+8f8FBfHusz/sr+G7u2nktU8RXltFqYhby2ME1nOZEBByOvYk8DmuOWT1lyc70npf010Ha+56f4Q/a4+EvxJ8Zx+GtA8Z+H7/U7oAW9lFlFvDtZiI9wCyEBTkKTjocEiul+JPjrw58GfCL61r13aaDpKzLC9wUKpubhc7QeTgflXnniz9lb4P8Aw61TQfE8fhqw8NX3ha4Eml3WkwtbO00kiKEl8sZkVnKph8gLI44BNfMv7U1n42+KnwM8Z+NtR8X3NzoMHjCfTLbQGKGwjt4JfIibymhLeZlQxPmc5J7kVvhMBSxNVckmo3V79/Kw1BNn32bjfEpQL8/ccGQHpXxjD+1V4b1n/gp/PpWm6h9uWz0SKS7YCVGtQllfT8IUy2VGfl9PXivr2N5xp1meBujQg+owK/G34n+Lr39m/wD4KaDxyqi40pYPsutx7Q7tbf2WY8qmUBKrcyHr2HBxg+zwrlaxTrwjrJQdvN3ROh+xXw9+IekfEnwmuu6XqSTaf581qZpN0W2WKVopEO8KQQ6sOR24z1rn/jvbtqNto1nFO2/Ub9B8j/fTBB74I+ccV8Ifsg/FLVf2l/iT4b8ER+JfEOheAfE2oa1rkMOlXLafd3C/atQkQGVMsuGC5XIH7sde/t37LP8Abfxh+NuveFPEniPXdV/4VTqzz2U8d88TTRLOsUSTsNvnf8erlgy4O89c4HLXyOWFqTnKXwK7XZXaXzvuGm59N/Fn4l6F8D/AF/4g1/UbaxsdPgebE8u3zyuMIoAJZmZlUBQTlhwc4r8ov23f2l/iL+05F4g+KXgWTXLTw54Z1JfD/hzS7G6uVj1y4iOyVz80ZDhJ7pjiIYFvjJ5r79/4Km+I9F8K/sPePdX1Syjv9QsdKkXSY5IzJGl1LJFHE5XIU7ZWiYbsgFc4PIPxp8Ivhwml/wDBOP4N6vfSnT7HWfEF5q2sSQudxvJ/7VbIVQQBhogAowAAO1dvDOGpU6TxlWPvc/L5bXaS76FQ0Vz610v/AIKaaDH+xn4h+IerQ2eg+IPCukP5uk6jPLG0uopYvcLB88aOSzxyJ8oJ+Q85r89PA/hm+8Eftcfs9eKfGuqazB8UfEnidrrxLZ3SSBdEhimt7a0gMjbiRJDG0hBk4E4+UA/NwFt8W5v2k/2hbT4XiU3OiXniOwg12AqYY5pPtM9q0ZOfm3pNKC2DkKPmHQ/oD/wVn/Z2g8efHH4I2vhyCx8N6zrOtPDJrFoq29xGwuNPCMZAjEkLkAlWxntXu4jL8JlONjQTtGspN9XGPLon83f7jLmlbU8d/wCCl/8AwVb8e+F/jXNpvgjSZf8AhD/hlqKwazrFje3Ma3k91aYhifZtBxJ9o4AfBi529/r79sb/AIKAL+zrpPw5m8PaHB4ofx9c2zPI4mW2sbGYZFx5ips3c8KzKSFY4wCR8Q/FbwP8PP2edP8Ajf8ADL4m6hqF1fam+j6jZ6pKhvbi/uY5VmmkMqxkjC3jAbkX5W2gcVS1j9r8w/sv+B/hz8bNPXw9460JNNk0m/hs451vdPitHt/9dA8zBvOBbDKnXOM8Dgr5dgatOhChTuob23mpJO/yd79kJqfLc/Tf9p/4jT/Bn4Nav4ls/sqy6Y1uS10D5KI9xFG7MQVxhHY5z2/CvmTx9/wVO8M2U1iy654ctfC+i2cNz4n8QG4keOC7mhiENnCowWZpZJ87DKVFo+4Dllg/4Kp/8FGfhJ4W/Zq8WeB5NcvL/wAVeKNNEWk2Vvp1yFml82PYGkZUVRuI5LDoa+Gv2fP2TNW0CHwd8SPj14cih/Z48Spu/snT78Sz3t29rKbS4uYUlZmAZZWHzkq04+UDITkynKcJLAyxGNfLNOyWzlotl1e9ulzVJ7yL+ifDTTv+ClXxG1Px98TvGWtfDTxI+s/ZfAcTWE8tiQ8rzwjzJcAHzJogFEkJ2xk4HVPoz4Wt4C/4J2+AfHGqeHNT1X4pfEXT4DLqviibQ7kQ26SNaf6MZkhkKhYFgbabk/6z7oyAPC/i5428X+Jf2hovD8nhyz0DSPCnitL7TtL0aw020gisormSNZ2ZDvZtqqoXfnCfdzg19Ux/Ce/t/wBkj9oa0k0i3mu5L5p4MGLfdImnaVIU3EjCkxuMMV6H1Br28xqU/wB3CrNeydvci1ZK6Wrtfa7a7ilVbR3Xh/8A4Kk+EtR8CeFLuys7jxDq93pkV3r1tYR3W7RC8UZDOBbu2HkcKucHnOTzXW/Gb9u/Tfhv4i0/TPDXhjU/H93qOlRa866QtxKtvp8jOouWaK3lXblRwSD8w49fhX4a/swat4U1SPxprHhjxdceHPG2gWVppen+HdehsJFuraG2WYXCi6hBjzFOy/O/IU8E19J3uneL/gD8UdCsPCngqy1vWpPhPbaZfWL3Ecv2MrMVUeZPcx7kDhlOJHJ+U4PJrw8XluXxrWoSvo3ura9L+RnBqR6B8Yf+Cnngr4deH9N1Hw2ll4xa+tzfNFFftbiG1SSdJZcmFt20wN8vDHIwDxmTVf2kdL/ah074OXPg/V/KfxK+oardW1rM++3W2t5IJY3yELKk8wXJA+ZVIFfK2q/8Et/iT4D8NeFtWuPD9p4vlt7KfStR0WDXfs8MRlmu2jYYltwY8yQFx5pyJH+Vug91/YF/ZD+JXwu+KY1Pxp4Z8KeHvDGk6Hc2/h+20u6Mr2Ul3cW00iON8nzYjbc245bPzNnNZVsPlVKl7ahO815rXpa33Mpb2PIf2dvHkf7dms+AfhhrHi7WdB0zwTBBq97ffapRP4hv42tbZrH99hXQKWYgCTJnHb73o/h39kyy/wCCiv7QHjbxt4t1/wAR6bZ6OU0TTdM0+VRawOtnaSLOFlV8NuupvuhfqMnO34B/4Jia94a+Ads1ubbw98U/D+sS63pV/pl6IVuW+zw7Led1Q74WuYUYof7ucjPO74h/Zs/aE+HnjGTxL8K7rwnpUniAKmr6FeT50+2k2iI3Mcew4fy4LbnzG6v8vOAVcZhZVJvBSUdLLm6a3ev978DRX6nzP4hv9ci0vx7+z5d+KtStNI0TxTa6fZ6nNdOLmO0RdRulBJcRjJjgGBtGAPlyBj7H03/gmr8N/hZ8WfBHjPQtVufBtz4Nk+aC3S2tYNfyAn7/AGRoXOCw6n/W47889L/wTLh8c/CfXZ/FmoTW/wAUfF93b6rq+s6dfsi291G8uVgPlEInlTPHjYcjHpurC0n9kb9pr4t+MLU/FH4lWFromgCT+y4vDl99ka/cqxikugtsPMxLHbtgkceZwc4PNisVSr/waigl8f8Aedldrvf5CPBtI/az8B+Nv+CiGnfFv/hOrRNRi1Oz8PjRobedoprCW2iiaUzdMCWZjtxjKDI71Y8efETxJF/wUz+JN74K+C2k/GqDVdPsplhvYUkhsIZLO0lWcb0IG7hQeOuK+l/Av/BJH4c+DP2c5vCY8P6S/iiaOYp4n2odThnMpkhdLjygw2bYwPk4C4we+NY/8E5fiH8P/HFtr/gn4m3ug6rPpcGk6pdNcxPJeQwQQRRZ3WTgn9wpJOD19SK9GWb5ZJ/ub6QdNc2isrNP3dQ16nNfGK61S0/bi/ZeudW8K2Pgi5kS4U6VZBRDal4o1KfJ8uQW2duFHGK9o/b6t2tdS+DV6quZIPiVowC7CTz9oX69Grg/ih/wTn8efFPTdAv9V+Keu3njHwzcvNp2svfxxzWSsYCQjJZjn9255U/e9+PX/AP7Ll3J4E0TTvH3irxB411TQdei8Q2t9d3iO8c8JzEuVhiGwDOV2/xHmvIq4vDwVGopJuCcWlfq5O+vTUZ7BbHzYldurqGIPYkZopT8q8UV87zdgJrqDN8/uxP60xZMxk7T17VYuZgs8g77j/OiFsrxWYEMQ/eE4x+FeVftzfDzUPit+yJ8Q9A0i2N5quo6NKtpb7GYzyr86qAqsxJKgDCk5xxXrBlw2B16mkEod/ftWlKpKnNTjuncTV1Y/P8A8NfBT41/tTfsq+Fvgx4h8J+HPh34W0vTrO3vNaupL+e/nFmihFW3e2hjBeRYycyHCq2ATjHNftEf8Esvin8XvjH8QbizufCF5pmvODot9q093nTYfJMYRIxbuquN0YykuP3HTkBP0lZ97bTQsyrvx2r1aGe4rD1PaULR3dt9Xu9SHSi9Gfjlb6trn7Ofww+IPwv0jx34d1ewvtetzqFjq8si+Jbq9F3HDKlpGs2Jk/cx/MyBifMyo4FfQZ/4Jb+J/jX4W0HxZZ+MrWxfVdK0q6/sLVLaX7G23TIIGW4UNy4ZSw+U4KJ6Zr7m1L4P+Gtf8dWXie70pZNd08AW919omXYAWYfIH2Hl26r3rop3Bf0zXdU4mxFk6PuyfxPTXbpby33GotPfQ+GYP+CS/iG/1jUZ73xf4Q09L7xHp3iKC20fR5I7eD7KtyGttpl+4ftIAIxwh4549f8Ajx+yL4u8ffEfxDr/AIL8a6f4Sj8aaVFpWtxz2kzTqsSTRLNbPFNHiURzN98NgonbIr6CM3zkUMw2GvKq5liqk+ecrv8A4b/JDcE3dnwbr3/BE7Utfhu7X/hbVxLY6qkMmo3V7pTXOqS3CpEGZZvtCjyy0S4VlJAyNxIzX1hefCyx1/4TL4A1oz6jbf2ONMlvDCuXAgELSoH3APhyRnOD611fjHxPb+DPDV1qd0SLe22lyF3H5nVRx9WFfPf7P/7bmrfGT9mXxbrs0NrD428LaVcX8sSW223DMtzJbcF2DApFGSN3Un8Np4nH4uknOXNGL08m/l5Boij4e/4J06lL8VfCmveLfil4h8XWHgyc3VhpE1uwtZ5Cd+ZxLNKGIkWN1KqpHlr3AYZPxm/4JZaV8XfHes6hL8QvGOkeHtavzqc3hyy2DT47ortaVUzs568oWyfvVueHP+CmPgPwZ8K/COp/EnWZtL8Q+J0maOG20yaVSi3klurfu1dQPlH8WeCcdK2fiJ/wU1+DHw0js/7X8UXUb6haw30Ij0m6fdBMu+NziPjI7dR6VaqZjCrondabf8DuFzufA3wkfwB4q8Qal/wkGu6quuvEyWl7Pvt9N8sMNsC/wq27kf7K18F/ttfCXwj+zT+3F8PfEurajdf8I74givLjWRdSwr5aC1S0ZY9wVOUCnDn7zehxX2F8Iv28/hh+0D4r17RPC+r39zfeGbF7+9afT5YYjACoaRCVycErwQG+boecflV+2J+3t4Y/b9/bp+Dusaf9uufgf4bvQkj3Fp9lu7za8U12xAYy7VZEAxsJ2NgHOT73C+CxVXGTjytJRlzdOj27sIavXY+nfAfw+1n9tXwPdeCfhh4Zl8HfD6x1++1LTfHetM4v5n86V3S1e3gEIgY3DIm2Y/IGznJFZH7Cvgyz+GfxwvPhr4+1STN9qkOuaBrunXK2z6pPDcC28mczA+Zv82OQiMk/N7iveh/wUi+HNr8OtO8H+DbXxDp9wtlFb6DJd2ita3MMLYYAmVpB8sU2PNVT8nuufFfE2p337X3wp8IeIvgx4Uv77XvhheoksmrTwW8c0kkMUh8tWuAGw9rF97aP3gxn5tvfha+IlhamHrrkpVHa76Na3bfnZBzJs9f/AG6dD1D9pn9vL4XfCZVMfh3R411nxI21pY5UZzcRwunKDcLAgeYMHzRgHFfSGpfs1+Bbj4QxeBb3TtKk8M2u2RLCeC38uPEm8OIynlg7yedn8R7mvjP9iNvFv7L/AOy/+0hrPxLMX/C4tEjSTVVg8uW1jjbTgNNCCLEZyXfdz35Iql+y3+z7o/7Rfx0sLDx5c6tNd+KPA6eLZ4rWSKFY/tVzHOiqVTgBZhxkkdCxxXi1MG+R041LQorda3e7a+8TqJpJH258M/2O/hv8MNGsLfRfCfhy3Wwu01CCddMtRI1wqoFm3JEvz/Ip3AA5716DqfhWx1y5s5ryzs7uexfzLeSWBZGhfIOUJBKnKryPQeleIfsu+A5/2ffjJ4l+HdtfSXXhZNJt9b0xJ9r3Fvmea3ZGdUTKiOKDg5Odx3V6T8efi/ZfAv4N+IfF+pSNHaaDYSXOViMhL9EG0dcuVHUdetfO4iNWpXSu5Sdrd3cSd1ct+Kvh14W8Za3BcatpPh7VtR0hmeF7u1hnms/MXaeWBZNy4HGMgCuZ8YeEvhp+0zol7pWsReCPHdrp4khmhlS11L+zcqUY4YOIiASORXwf8N/Hl943sf2gfEmp61FpbeNLXR9ZtLxrfKw2z3kUkKlEjcg+VNEpBVuc8964XTPiHe/s3eGPFd1c+FI/Alxrvwxks7ZVl+2/20uyQmf/AI+LgRnJXgmIfP8Ac44+ijw7WVTkhUvNW/FJv7ru5mqysffX7OX7OvwL+Hpuv+Fe6V8P769gmUzXdrb6fPdwuVJUb4I1I+VmxnsTXYfGX41eDfgXpdjL4w1vSdHttQkaK2W8uoIVkKAEhRK6A4BHTOMivjL9iTS7L4X/ALTHgmz8U+D7bwrq2t2NwnhOWwupblLyGNb43H2jdcTbWV3kC8LkMOuMj2jx14c0740/8FDbXwr4lsjfaRpPhy/urSPzGiAlYaUSd0bBzw7cHjmuGtgEsW41ZOSSu3107dDVanqvxg/am8BfA/RNH1PxD4h0q2t9dUtYOl5br9qQKrfIXkUMMOv3SfvD1rB1f9vL4d6V8G9K8czao/8AZGqXn2CzhWe2+0zyb5FO1TNtIHlyE4YnCNxwcfA/gL9mX4xfHyw05PhdB4Xkn+FPifUrItrVwYltnQWHkoNvMgBt+Sc9OvNfT/7Pfibxp+1p+ztqHia+0zw5p3x98MS3ei2UhaWPTIJGi8yP5VkkVs216Rk5+ZjwMA1043KcPRhCSnzNP3l1V9vlbdmbk7tXPqH4VfEnSPjF4PtNe8PXy3dhqMYkULMjtHyylW2MwDBlYEZOCpHavE/Av7bXww8WftUX1tZQapHrfkjwz/bTG0/s6d1vCBbLKJN5kLvvCZyV52565/8AwTD1C30/TfG3hvUY3j8f+H9YuG8YPHzaS3k99fyhrc5IKEmQ9BgEcenw34a0zXbTxbYeNo4ILb4Tf8LiVotN3Br2TUd6zGY8lvL+zBVx5o+Y/d/ip4LK6dadWEpPRK3nft3/AKZSlaOu5+qXjv466B8OviZ4X8LX0rf214suRbWcMbxhkzHO4dgWDbf9HccKeSPfEfxo/aG0P4J+IvB2k6tl7rxne3NnahZY18ryLaS4eRwxBK4jC8d5FzjNfmj/AMNJ6N43/bi8LfEfxzY+JV8V23iTT7G0gs47UWUdn5CKvyiQsZDM8hJLkYb2AHF/th/tB+J/F37Z2reM/E2lXsXhPS9VmtPDqRraiQQtbNCdyrKWLMIY2+Y8fN0ztr0cNwhGdWFKU0o8jk9ftdIrXXoR7TSx92ftG/8ABUnW/wBmzxreWGsfBTxjLoMVzJY2msK0kUd9MskiqIy0AQhkQuMOTg9COa+tNCvJtU0yGaWB7Z5ASY5M7kwxHOQPTP418rfteeGG/aS/an+CXhmS2lOk6XCPG1xE0ixOjrd2caAsCc4VpQVXj36V9awyk/f45r5fFwoxo0nGNptO+t+uhrFNbg8J4OV49qfsOR0OO9PDD1qIyZbB78CvN1LHGLZSFc96c3vTRL270ACRZBppjEZyO3anmby0LNwB1pGO6X8KAEjTcM0UnmOZduOB0ooAkvCWv2HT5j/M06P5I8dafcpvuX/3jSKAi4pAM24l/Co2j2yDmrGAxpGjywpgQnOf60MNzCrG0U10oAYF2j6c1S1m0/tO3aNJngY4xIjEMuPoR/OtFMFCKa0QB4FAFOO22wRjfvZAAxbq3vTmh/0gKBjNWBAA2cc04r82e9O7A+ZP+CqlprfiT9mJvC3hxb1tZ8Vata2UJtkZzEIw92zMFBbbi2I4HVh2zXgPiT4O+Mv2BfFeoyeIdY1P4n2nxZ0WfwwP7L00oNOkVYIoPMGSNnlM6jBBxHwDzj9GcFeR1ximxBofujHGK9GhmtWjS9jFe712126/IzlFyufihpHhTxJ4G0fwrreu2HxW0jStc8OXUEdjpelXE87yRXWoo0ExaaEx7/Ni2gFiROeBkb/VP2TPgLqK/FbVL2Xwr4rWw17wQLq1Os6fcb42fU7ZhE/mF8SbEZ9oY8E445r9XRcujswbDN14HNU71GmQg8gtuP1rtlxJiJxeglSsrH4zf8FAvAXj0fDX9nDwt4TS98Ka/wCOvC7+Fb1Y7eSCaJJ7fSoGgmCx71G8rkAbvk6Zrzr9rGw8ZW9j8JPD/hr4d614Hh+E7zo893pkkEZuL+/WaOWImE5jUsgYsRyHAU45/Rn40Wc3xJ/4KT+D9KCR3EXhWFtSKq214gZdIcs3PPXpWB/wWn/ZotPib8JbLxxBdTw+KfC0cdtYRiYLb3QkvbYBXUoxON79Cv3uc8V9TlWeclfCUZxS3d7b819/kzayVkz5J/Zgi+If7Tf7bngfT59J8bXdr4I0pxruo6qLuTSprkWMwBtlw0SoRewBcCMffwoz836RfsC/DbxF8Nv2dbTRPEttNaanYyKjeYsi7wttboXAdVOCyN27flof8E+/hfH8Mf2QPAsDweTqGpaVb6lqGJGdWuJokZyM9B04HAr2ncrnGR6818xn2bzxNaWHivci7L5NkNO9z5T/AGqP2RPFHxh/aQ8J61o1/Y23g3U2sk8b2Eyy7tVjsLo3FuDtRgfvsvLR8DneOBU+IHwM+JPw1/bKg8cfDrSNIu/D/wDwh8Hh1bWWWaH7OY3BG0razrgJFGAMg/N+f13GFmbsT9adgYxjoa85ZlXjFR0atb1T7kKnbVHzD8MvgZ8Y/DUXirxhquueH9Q+IfiG3isbHhlt9NtE+0TCEn7Ngnz5x/ywzhOv8A90+Jnwc8N/G3wVdeHvF+kwa5o1+Atxayu6q4Dqw5Ug/eRTwR0rrAq7cUMoSuN1puftU7NWtbS1h8mlj4u13/gi/wDD/WfGvjGT7PYaf4P16ytrTTNMgNyZtKeJ7d2cMJlY7jDJ/EOJe/Sr3gH/AIJ2eL/GHiS/m+OfjPSfidpllokugeHLUWBiOmxSMheZiuz5ysUY53Hj7/r9hbs0dBXf/bGMesptvu9WvR7+vcpQjY+Uv2cv+Ce/iD4Z/Fmx8WfEDx7H8Qrvw3GYfDQexaFtISRZxPg+YRl3mzyCfkAz0x3v7Vn7K2rfHWPRtR8JeMrn4eeMNEaVLbXLWB5ZDbzCMTQMBIgIbyoj827HljGK9v8ALzjimyEInTvWE8fXnUVWT1Wn9Io+TtX/AOCVmi6d8PvDFp4Q8U6r4J8VaApW58Q6a92txqheOESmRVulzvkt4pCWZuV9yTq+H/8AgmR4R8JfCDSvDei6nqWla/pGpnVYvE9vNdrqDSkOhBYXPmEGFzFhpSNoHHAA+nEAZaUuIxRLMMRJcrm7XuRyR7HA/A/4AaP8BPD7waWhn1K/xLqmpzGRrnVZtzuZZWd3YsWlkPLHG49q4GX/AIJr/COX4nJ4p/4Ra3F0L/8Atk2pnuTam/8AN837V5PneUJM8ZEfTjpxXv2/zFz/AA+1AILVnHF1oyc4Sab3H7NMwPF/w+0rx8dMGuWUWqDRr+LVbEyg/wCjXUWRHKMHqu5sZ45pPHnw00X4o6HDpniTTbfWdMimE6W1wCVSRVZQw9CAzD8TXROu1cDpmmKcZ9vSsVJrboOxlr4J0r/hLf7fNhbnXBa/YPt5T999m3+Z5Wf7u/5vrWmqZaorq9FpDu8uaYZxiFN7D3xU6yEAbvWpGOK5XFV3jLlD/cNWSwAqMspfPNADJVYHbn3zRjp6jr71IDs4/Sm8MfegBSpLZpNuWB9O9KzeWuT0oD7uP0oACMnNFBcJ2P4CigCzKf8ASZP940jLuNLcAid/TcaGGDSARV20tFFMAooooAbt280qnIpaKACmyU6igBM4Wm7+afSYoAiZc81FLkrxU7jk1DKMLzQB8oeFfCk9n/wVZ8S387GS2uvDJFuCDiEj+yMjnjkj9Ks/8FR9SA+FmgaTzu1bVbWIIOsmNQseMde/au9/al8R3PwjttN8aaVoaapLYXBj1GXySWtrTaJZJSVG7aogXPUdPQV4d8SdQt/2v/8Ago58NJfDijxB4P8AhvCL3UNStD59nHcTCaVUckbA2baLpk/MOnFfRYO7qU8VL4YL8YrT7w33PrH4J6f/AGX8FPCFsRsMGi2cZX+7iBOK6FUG31PrUqWypgIAqDhVAwAOwxUhtgB/9avBlPmk5d9RWKkMTwjIfvzip4mJB781J9nUEU9YRt4FZjGA5NIVY9al8vaetKeaAIVb5sY/GiN93WpDGS3AoWPa3IoAjZiDTHbcnSppYcHpTGg+WgCKKQrw397HFE67wf7vapki2j1/Cn/Z1K4PSgCtGpVcBvpntT8c4J59qm+zhhgfypVQRk8UANiJKU1Ru3fXmpAMCnNgLQBBAwWPPTt1xSB8yY61MiArgAYo2c9P0oAjxk+3pTdmyTA6Hv6VOI8dqBx2oAjOd/8AWmHar5qfy+elRi2zISaACZwMA8g1Er/vOBxjrVkrx0pFjwOlAFYOTJ7YoqyIFVsnrRQBovY72b5upz0pv9m/7f6UUVF2Af2b/t/pR/Zv+3+lFFF2Af2b/t/pR/Zv+3+lFFF2Af2b/t/pR/Zv+3+lFFF2Af2b/t/pR/Zv+3+lFFF2Af2b/t/pR/Zv+3+lFFF2A06Vk/f/APHaa+jbx/rP/Hf/AK9FFF2BQ1rwHaeItOuLK+SC7sbuNoZ7eaEPHKjDaykHqCCR+Nc18IP2YvCHwFsLyDwnpFrpA1GRZbp1DyyTso2rl5GZsAZAGcDJ45NFFWqs1FxT0YHaDRcD/Wf+O/8A16d/ZP8A00/8dooqLsAOk5H+s/8AHaVNL2Ljf/47RRRdgJ/ZP/TT/wAdo/sn/pp/47RRRdgKmmbG+/8A+O0Ppm8/f/8AHaKKLsBZNN8xfv8A6U3+yvlH7zp/s0UUXYB/ZP8A00/8do/sn/pp/wCO0UUXYCppmxvv/wDjtI+lb2z5mP8AgNFFF2Af2T/00/8AHaG0ndj5+n+zRRRdgKNL2/x/pR/ZfzZ3/wDjtFFF2Av9m/7f6U3+yufv/wDjtFFF2A7+zf8Ab/SkOmZH3/0ooouwA6Zlcb//AB2lXTNv8f6UUUXYCNpe5vv/APjtFFFF2B//2Q==" alt="company_logo" width="100" height="100"/>
								</td>

								<td style="width: 30%;">
									<table style="width:100%; border-collapse: collapse;">
										<tbody>
											<tr>
												<td id="invoice-info-td" style="width: 50%;">
													<span style="font-weight:bold; ">
														<xsl:text>Özelleştirme No:</xsl:text>
													</span>
												</td>
												<td id="invoice-info-td" style="width: 50%;">
													<xsl:for-each select="n1:Invoice/cbc:CustomizationID">
														<xsl:apply-templates/>
													</xsl:for-each>
												</td>
											</tr>
											<tr style="height:13px; ">
												<td id="invoice-info-td" style="width: 50%;">
													<span style="font-weight:bold; ">
														<xsl:text>Senaryo:</xsl:text>
													</span>
												</td>
												<td id="invoice-info-td" style="width: 50%;">
													<xsl:for-each select="n1:Invoice/cbc:ProfileID">
														<xsl:apply-templates/>
													</xsl:for-each>
												</td>
											</tr>
											<xsl:if test="not(//n1:Invoice/cbc:ProfileID='EGIDERPUSULASI')">
												<tr style="height:13px; ">
													<td id="invoice-info-td" style="width: 50%;">
														<span style="font-weight:bold; ">
															<xsl:text>Fatura Tipi:</xsl:text>
														</span>
													</td>
													<td id="invoice-info-td" style="width: 50%;">
														<xsl:for-each select="n1:Invoice/cbc:InvoiceTypeCode">
															<xsl:apply-templates/>
														</xsl:for-each>
													</td>
												</tr>
											</xsl:if>

											<xsl:if test="//n1:Invoice/cbc:AccountingCost">
												<tr style="height:13px; ">
													<td id="invoice-info-td" style="width: 50%;">
														<span style="font-weight:bold; ">
															<xsl:text>İlave Fatura Tipi:</xsl:text>
														</span>
													</td>
													<td id="invoice-info-td" style="width: 50%;">
														<xsl:for-each select="n1:Invoice/cbc:AccountingCost">
															<xsl:apply-templates/>
														</xsl:for-each>
													</td>
												</tr>
											</xsl:if>
											<tr style="height:13px; ">
												<td id="invoice-info-td" style="width: 50%;">
													<xsl:choose>
														<xsl:when test="//n1:Invoice/cbc:ProfileID='EGIDERPUSULASI'">
															<span style="font-weight:bold; ">
																<xsl:text>Pusula No:</xsl:text>
															</span>
														</xsl:when>
														<xsl:otherwise>
															<span style="font-weight:bold; ">
																<xsl:text>Fatura No:</xsl:text>
															</span>
														</xsl:otherwise>
													</xsl:choose>
												</td>
												<td id="invoice-info-td" style="width: 50%;">
													<xsl:for-each select="n1:Invoice/cbc:ID">
														<xsl:apply-templates/>
													</xsl:for-each>
												</td>
											</tr>
											<tr style="height:13px; ">
												<td id="invoice-info-td" style="width: 50%;">
													<xsl:choose>
														<xsl:when test="//n1:Invoice/cbc:ProfileID='EGIDERPUSULASI'">
															<span style="font-weight:bold; ">
																<xsl:text>Pusula Tarihi:</xsl:text>
															</span>
														</xsl:when>
														<xsl:otherwise>
															<span style="font-weight:bold; ">
																<xsl:text>Fatura Tarihi:</xsl:text>
															</span>
														</xsl:otherwise>
													</xsl:choose>
												</td>
												<td id="invoice-info-td" style="width: 50%;">
													<xsl:for-each select="n1:Invoice/cbc:IssueDate">
														<xsl:apply-templates select="."/>
														<xsl:text>&#160;</xsl:text>
														<xsl:value-of select="substring(../cbc:IssueTime,1,5)"/>
													</xsl:for-each>
												</td>
											</tr>
											<xsl:for-each select="//n1:Invoice/cac:AdditionalDocumentReference/cbc:DocumentTypeCode[text()='MUKELLEF_KODU' or text()='MUKELLEF_ADI' or text()='DOSYA_NO']">
												<tr style="height:13px; ">
													<td id="invoice-info-td" style="width: 50%;">
														<span style="font-weight:bold;">
															<xsl:if	test="../cbc:DocumentTypeCode='MUKELLEF_KODU'">
																<xsl:text>Mükellef Kodu:</xsl:text>
															</xsl:if>
															<xsl:if	test="../cbc:DocumentTypeCode='MUKELLEF_ADI'">
																<xsl:text>Mükellef Adı:</xsl:text>
															</xsl:if>
															<xsl:if	test="../cbc:DocumentTypeCode='DOSYA_NO'">
																<xsl:text>Dosya No:</xsl:text>
															</xsl:if>
														</span>
													</td>
													<td id="invoice-info-td" style="width: 50%;">
														<xsl:value-of select="../cbc:DocumentType"/>
													</td>
												</tr>
											</xsl:for-each>
											<xsl:if test="(//n1:Invoice/cbc:AccountingCost) and (//n1:Invoice/cac:InvoicePeriod)">
												<tr style="height:13px; ">
													<td id="invoice-info-td" style="width: 50%;">
														<span style="font-weight:bold;">
															<xsl:text>Dönem Başlangıcı:</xsl:text>
														</span>
													</td>
													<td id="invoice-info-td" style="width: 50%;">
														<xsl:for-each select="//n1:Invoice/cac:InvoicePeriod">
															<xsl:apply-templates select="cbc:StartDate"/>
														</xsl:for-each>
													</td>
												</tr>
												<tr style="height:13px; ">
													<td id="invoice-info-td" style="width: 50%;">
														<span style="font-weight:bold;">
															<xsl:text>Dönem Bitişi:</xsl:text>
														</span>
													</td>
													<td id="invoice-info-td" style="width: 50%;">
														<xsl:for-each select="//n1:Invoice/cac:InvoicePeriod">
															<xsl:apply-templates select="cbc:EndDate"/>
														</xsl:for-each>
													</td>
												</tr>
											</xsl:if>
											<xsl:for-each select="n1:Invoice/cac:DespatchDocumentReference">
												<tr style="height:13px; ">
													<td id="invoice-info-td" style="width: 50%;">
														<span style="font-weight:bold; ">
															<xsl:text>İrsaliye No:</xsl:text>
														</span>
														<xsl:text>&#160;</xsl:text>
													</td>
													<td id="invoice-info-td" style="width: 50%;">
														<xsl:value-of select="cbc:ID"/>
													</td>
												</tr>
												<tr style="height:13px; ">
													<td id="invoice-info-td" style="width: 50%;">
														<span style="font-weight:bold; ">
															<xsl:text>İrsaliye Tarihi:</xsl:text>
														</span>
													</td>
													<td id="invoice-info-td" style="width: 50%;">
														<xsl:for-each select="cbc:IssueDate">
															<xsl:apply-templates select="."/>
														</xsl:for-each>
													</td>
												</tr>
											</xsl:for-each>
											<xsl:if test="//n1:Invoice/cbc:paymentDueDate">
												<tr style="height:13px; ">
													<td id="invoice-info-td" style="width: 50%;">
														<span style="font-weight:bold; ">
															<xsl:text>Son Ödeme Tarihi:</xsl:text>
														</span>
													</td>
													<td id="invoice-info-td" style="width: 50%;">
														<xsl:for-each select="n1:Invoice/cbc:paymentDueDate">
															<xsl:apply-templates/>
														</xsl:for-each>
													</td>
												</tr>
											</xsl:if>
											<xsl:if test="//n1:Invoice/cac:OrderReference">
												<tr style="height:13px">
													<td id="invoice-info-td" style="width: 50%;">
														<span style="font-weight:bold; ">
															<xsl:text>Sipariş No:</xsl:text>
														</span>
													</td>
													<td id="invoice-info-td" style="width: 50%;">
														<xsl:for-each select="n1:Invoice/cac:OrderReference/cbc:ID">
															<xsl:apply-templates/>
														</xsl:for-each>
													</td>
												</tr>
											</xsl:if>
											<xsl:if	test="//n1:Invoice/cac:OrderReference/cbc:IssueDate">
												<tr style="height:13px">
													<td id="invoice-info-td" style="width: 50%;">
														<span style="font-weight:bold; ">
															<xsl:text>Sipariş Tarihi:</xsl:text>
														</span>
													</td>
													<td id="invoice-info-td" style="width: 50%;">
														<xsl:for-each select="n1:Invoice/cac:OrderReference/cbc:IssueDate">
															<xsl:apply-templates select="."/>
														</xsl:for-each>
													</td>
												</tr>
											</xsl:if>
											<xsl:if	test="n1:Invoice/cac:AccountingCustomerParty/cac:Party/cac:PartyIdentification/cbc:ID[@schemeID='VKN' and text()='7350019759']">
												<tr style="height:13px">
													<td id="invoice-info-td" style="width: 50%;">
														<span style="font-weight:bold; ">
															<xsl:text>Sipariş Sorumlusu:</xsl:text>
														</span>
													</td>
													<td id="invoice-info-td" style="width: 50%;">
														<xsl:value-of select="$varsiparissorumlusu"/>
													</td>
												</tr>
											</xsl:if>
											<xsl:for-each select="n1:Invoice/cac:ReceiptDocumentReference">
												<tr style="height:13px; ">
													<td id="invoice-info-td" style="width: 50%;">
														<span style="font-weight:bold; ">
															<xsl:text>Mal Kabul No:</xsl:text>
														</span>
														<xsl:text>&#160;</xsl:text>
													</td>
													<td id="invoice-info-td" style="width: 50%;">
														<xsl:value-of select="cbc:ID"/>
													</td>
												</tr>
											</xsl:for-each>
											<xsl:for-each select="n1:Invoice/cac:TaxRepresentativeParty/cac:PartyIdentification/cbc:ID[@schemeID='ARACIKURUMVKN']">
												<tr>
													<td id="invoice-info-td" style="width: 50%;">
														<span style="font-weight:bold; ">
															<xsl:text>Aracı Kurum VKN:</xsl:text>
														</span>
													</td>
													<td id="invoice-info-td" style="width: 50%;">
														<xsl:value-of select="."/>
													</td>
												</tr>
												<tr>
													<td id="invoice-info-td" style="width: 50%;">
														<span style="font-weight:bold; ">
															<xsl:text>Aracı Kurum Unvan:</xsl:text>
														</span>
													</td>
													<td id="invoice-info-td" style="width: 50%;">
														<xsl:value-of select="../../cac:PartyName/cbc:Name"/>
													</td>
												</tr>
											</xsl:for-each>
											<!--											<xsl:if	test="//n1:Invoice/cac:PaymentMeans/cbc:PaymentMeansCode">-->
											<!--												<tr style="height:13px">-->
											<!--													<td id="invoice-info-td" style="width: 50%;">-->
											<!--														<span style="font-weight:bold; ">-->
											<!--															<xsl:text>Ödeme Şekli:</xsl:text>-->
											<!--														</span>-->
											<!--													</td>-->
											<!--													<td id="invoice-info-td" style="width: 50%;">-->
											<!--														<xsl:for-each select="n1:Invoice/cac:PaymentMeans/cbc:PaymentMeansCode">-->
											<!--															<xsl:call-template name="PaymentMeansCode">-->
											<!--																<xsl:with-param name="PaymentMeansCodeType">-->
											<!--																	<xsl:value-of select="."/>-->
											<!--																</xsl:with-param>-->
											<!--															</xsl:call-template>-->
											<!--														</xsl:for-each>-->
											<!--													</td>-->
											<!--												</tr>-->
											<!--											</xsl:if>-->
											<xsl:if	test="//n1:Invoice/cac:PaymentMeans/cbc:PaymentDueDate">
												<tr style="height:13px">
													<td id="invoice-info-td" style="width: 50%;">
														<span style="font-weight:bold; ">
															<xsl:text>Ödeme Tarihi:</xsl:text>
														</span>
													</td>
													<td id="invoice-info-td" style="width: 50%;">
														<xsl:for-each select="n1:Invoice/cac:PaymentMeans/cbc:PaymentDueDate">
															<xsl:value-of select="substring(.,9,2)"/>-<xsl:value-of select="substring(.,6,2)"/>-<xsl:value-of select="substring(.,1,4)"/>
														</xsl:for-each>
													</td>
												</tr>
											</xsl:if>
										</tbody>
									</table>
								</td>
							</tr>
						</tbody>
					</table>



					<!-- ETTN SATIRI -->
					<table style="width: 40%; margin-bottom: 5px;">
						<tr>
							<td style="width: 100%;">
								<span style="font-weight:bold; ">
									<xsl:text>ETTN:</xsl:text>
								</span>
								&#160;
								<xsl:for-each select="n1:Invoice/cbc:UUID">
									<xsl:apply-templates/>
								</xsl:for-each>
							</td>
						</tr>
					</table>

					<!-- URUNLER SATIRI (TABLOSU) -->
					<table style="width: 100%; border-collapse: collapse; border-style: solid; border-width: 2px;">
						<tbody>
							<tr>
								<td id="invoice-line-td" style="width:3%">
									<span style="font-weight:bold;">
										<xsl:text>Sıra No</xsl:text>
									</span>
								</td>
								<xsl:choose>
									<xsl:when test="$varItemCode &gt; 0">
										<td id="invoice-line-td" style="width:7%">
											<span style="font-weight:bold;">
												<xsl:text>Ürün Kodu</xsl:text>
											</span>
										</td>
									</xsl:when>
									<xsl:otherwise>
									</xsl:otherwise>
								</xsl:choose>
								<xsl:choose>
									<xsl:when test="//n1:Invoice/cac:AccountingCustomerParty/cac:Party/cac:PartyIdentification/cbc:ID[@schemeID='VKN' and text()='7350019759']">
										<td id="invoice-line-td" style="width:7%">
											<span style="font-weight:bold;">
												<xsl:text>Sipariş Satır No</xsl:text>
											</span>
										</td>
									</xsl:when>
								</xsl:choose>

								<xsl:if test="$varfaturatipi='SGK'">
									<td id="invoice-line-td" style="width:80%">
										<span style="font-weight:bold;">
											<xsl:text>Açıklama</xsl:text>
										</span>
									</td>
								</xsl:if>
								<xsl:if test="not($varfaturatipi='SGK')">
									<xsl:if test="not(//n1:Invoice/cbc:InvoiceTypeCode='TEVKIFATIADE')">
										<td id="invoice-line-td" style="width:20%">
											<span style="font-weight:bold;">
												<xsl:text>Mal Hizmet</xsl:text>
											</span>
										</td>
									</xsl:if>

									<xsl:if test="//n1:Invoice/cbc:InvoiceTypeCode='TEVKIFATIADE'">
										<td id="invoice-line-td" style="width:10.6%">
											<span style="font-weight:bold;">
												<xsl:text>İade Edilen Mal Hizmet</xsl:text>
											</span>
										</td>
									</xsl:if>

									<td id="invoice-line-td" style="width:7.4%">
										<span style="font-weight:bold;">
											<xsl:text>Miktar</xsl:text>
										</span>
									</td>
									<xsl:if test="$varEtiketFiyati='1'">
										<td id="invoice-line-td" class="table-background table-header" style="width:10%; border-color: #c9c9c9">
											<span style="font-weight:bold;">
												<xsl:text>Etiket Fiyatı</xsl:text>
											</span>
										</td>
									</xsl:if>
									<xsl:if test="$varDepocuFiyati='1'">
										<td id="invoice-line-td" class="table-background table-header" style="width:9%; border-color: #c9c9c9">
											<span style="font-weight:bold;">
												<xsl:text>Depocu Fiyatı</xsl:text>
											</span>
										</td>
									</xsl:if>

									<td id="invoice-line-td" class="table-background table-header" style="width:9%; border-color: #c9c9c9">
										<span style="font-weight:bold;">
											<xsl:text>Birim Fiyat</xsl:text>
										</span>
									</td>
									<xsl:if test="$varEczaciKar='1'">
										<td id="invoice-line-td" class="table-background table-header" style="width:10%; border-color: #c9c9c9">
											<span style="font-weight:bold;">
												<xsl:text>Eczacı Kâr Oranı.</xsl:text>
											</span>
										</td>
									</xsl:if>

									<xsl:if test="$varKurumIskonto='1'">
										<td id="invoice-line-td" class="table-background table-header" style="width:10%; border-color: #c9c9c9">
											<span style="font-weight:bold;">
												<xsl:text>Kurum İskontosu</xsl:text>
											</span>
										</td>
									</xsl:if>

									<xsl:if test="$varVade='1'">
										<td id="invoice-line-td" class="table-background table-header" style="width:10%; border-color: #c9c9c9">
											<span style="font-weight:bold;">
												<xsl:text>Vade Tarihi</xsl:text>
											</span>
										</td>
									</xsl:if>
									<xsl:if test="$varAllowanceRate &gt; 0">
										<td id="invoice-line-td" style="width:7%">
											<span style="font-weight:bold;">
												<xsl:text>İskonto/ Arttırım Oranı</xsl:text>
											</span>
										</td>
									</xsl:if>
									<xsl:if test="$varAllowanceAmount &gt; 0">
										<td id="invoice-line-td" style="width:9%">
											<span style="font-weight:bold;">
												<xsl:text>İskonto/ Arttırım Tutarı</xsl:text>
											</span>
										</td>
									</xsl:if>
									<xsl:if test="$varAllowanceReason &gt; 0">
										<td id="invoice-line-td" style="width:9%">
											<span style="font-weight:bold;">
												<xsl:text>İskonto/ Arttırım Nedeni</xsl:text>
											</span>
										</td>
									</xsl:if>
									<xsl:if test="not(//n1:Invoice/cbc:InvoiceTypeCode='TEVKIFATIADE')">
										<td id="invoice-line-td" style="width:7%">
											<span style="font-weight:bold;">
												<xsl:text>KDV Oranı</xsl:text>
											</span>
										</td>
									</xsl:if>
									<xsl:if test="not(//n1:Invoice/cbc:InvoiceTypeCode='TEVKIFATIADE')">
										<td id="invoice-line-td" style="width:10%">
											<span style="font-weight:bold;">
												<xsl:text>KDV Tutarı</xsl:text>
											</span>
										</td>
									</xsl:if>
									<xsl:if test="//n1:Invoice/cac:InvoiceLine/cac:OrderLineReference/cac:OrderReference">
										<td id="invoice-line-td" style="width:10%">
											<span style="font-weight:bold;">
												<xsl:text>Sipariş No</xsl:text>
											</span>
										</td>
									</xsl:if>
									<xsl:if test="//n1:Invoice/cac:InvoiceLine/cac:DespatchLineReference/cac:DocumentReference">
										<td id="invoice-line-td" style="width:10%">
											<span style="font-weight:bold;">
												<xsl:text>İrsaliye No</xsl:text>
											</span>
										</td>
									</xsl:if>
									<xsl:if test="not(//n1:Invoice/cbc:InvoiceTypeCode='TEVKIFATIADE')">
										<td id="invoice-line-td" style="width:17%; ">
											<span style="font-weight:bold;">
												<xsl:text>Diğer Vergiler</xsl:text>
											</span>
										</td>
									</xsl:if>
									<xsl:if test="$varLineExplanation &gt; 0">
										<td id="invoice-line-td" style="width:10.6%">
											<span style="font-weight:bold;">
												<xsl:text>Satır Açıklaması</xsl:text>
											</span>
										</td>
									</xsl:if>
								</xsl:if>

								<xsl:if test="//n1:Invoice/cbc:InvoiceTypeCode='TEVKIFATIADE'">
									<td id="invoice-line-td" style="width:10.6%">
										<span style="font-weight:bold;">
											<xsl:text>İade Edilen Mal Oranı (%)</xsl:text>
										</span>
									</td>
								</xsl:if>

								<xsl:if test="//n1:Invoice/cbc:InvoiceTypeCode='TEVKIFATIADE'">
									<td id="invoice-line-td" style="width:10.6%">
										<span style="font-weight:bold;">
											<xsl:text>İadeye Konu KDV Tutarı</xsl:text>
										</span>
									</td>
								</xsl:if>
								<xsl:if test="//n1:Invoice/cbc:InvoiceTypeCode='TEVKIFATIADE'">
									<td id="invoice-line-td" style="width:17%; ">
										<span style="font-weight:bold;">
											<xsl:text>Diğer Vergiler</xsl:text>
										</span>
									</td>
								</xsl:if>
								<xsl:if test="not(//n1:Invoice/cbc:InvoiceTypeCode='TEVKIFATIADE')">
									<td id="invoice-line-td" style="width:10.6%">
										<span style="font-weight:bold;">
											<xsl:text>Mal Hizmet Tutarı</xsl:text>
										</span>
									</td>
								</xsl:if>

								<xsl:if test="//n1:Invoice/cbc:InvoiceTypeCode='TEVKIFATIADE'">
									<td id="invoice-line-td" style="width:10.6%">
										<span style="font-weight:bold;">
											<xsl:text>İadeye Konu İşlem Bedeli</xsl:text>
										</span>
									</td>
								</xsl:if>

								<xsl:if test="//n1:Invoice/cbc:InvoiceTypeCode='TEVKIFATIADE'">
									<td id="invoice-line-td" style="width:10.6%">
										<span style="font-weight:bold;">
											<xsl:text>Alıştaki Tevkifatsız KDV Tutarı</xsl:text>
										</span>
									</td>
								</xsl:if>

								<xsl:if test="//n1:Invoice/cbc:ProfileID='EARSIVFATURA' and //n1:Invoice/cbc:InvoiceTypeCode='ISTISNA'">
									<td id="invoice-line-td" style="width:10.6%">
										<span style="font-weight:bold;">
											<xsl:text>GTIP</xsl:text>
										</span>
									</td>
								</xsl:if>

								<xsl:if test="//n1:Invoice/cbc:ProfileID='HKS' or /n1:Invoice/cbc:InvoiceTypeCode='HKSSATIS' or /n1:Invoice/cbc:InvoiceTypeCode='HKSKOMISYONCU'">
									<td id="invoice-line-td" style="width:5%">
										<span style="font-weight:bold;">
											<xsl:text>Künye Numarası</xsl:text>
										</span>
									</td>
								</xsl:if>

								<xsl:if test="//n1:Invoice/cbc:ProfileID='HKS' and /n1:Invoice/cbc:InvoiceTypeCode='SATIS'">
									<td id="invoice-line-td" style="width:5%">
										<span style="font-weight:bold;">
											<xsl:text>Mal Sahibi VKN/TCKN</xsl:text>
										</span>
									</td>

									<td id="invoice-line-td" style="width:5%">
										<span style="font-weight:bold;">
											<xsl:text>Mal Sahibi Ad/Soyad</xsl:text>
										</span>
									</td>
								</xsl:if>

								<xsl:if test="//n1:Invoice/cbc:InvoiceTypeCode='HKSSATIS'">
									<td id="invoice-line-td" style="width:5%">
										<span style="font-weight:bold;">
											<xsl:text>Mal Sahibi VKN/TCKN</xsl:text>
										</span>
									</td>

									<td id="invoice-line-td" style="width:5%">
										<span style="font-weight:bold;">
											<xsl:text>Mal Sahibi Ad/Soyad</xsl:text>
										</span>
									</td>
								</xsl:if>

								<xsl:if test="//n1:Invoice/cbc:ProfileID='IHRACAT' or //n1:Invoice/cbc:ProfileID='OZELFATURA'">
									<td id="invoice-line-td" style="width:10.6%">
										<span style="font-weight:bold;">
											<xsl:text>Teslim Şartı</xsl:text>
										</span>
									</td>

									<td id="invoice-line-td" style="width:10.6%">
										<span style="font-weight:bold;">
											<xsl:text>Eşya Kap Cinsi</xsl:text>
										</span>
									</td>

									<td id="invoice-line-td" style="width:10.6%">
										<span style="font-weight:bold;">
											<xsl:text>Kap No</xsl:text>
										</span>
									</td>

									<td id="invoice-line-td" style="width:10.6%">
										<span style="font-weight:bold;">
											<xsl:text>Kap Adet</xsl:text>
										</span>
									</td>

									<td id="invoice-line-td" style="width:10.6%">
										<span style="font-weight:bold;">
											<xsl:text>Teslim/Bedel Ödeme Yeri</xsl:text>
										</span>
									</td>

									<td id="invoice-line-td" style="width:10.6%">
										<span style="font-weight:bold;">
											<xsl:text>Gönderilme Şekli</xsl:text>
										</span>
									</td>

									<td id="invoice-line-td" style="width:10.6%">
										<span style="font-weight:bold;">
											<xsl:text>GTİP</xsl:text>
										</span>
									</td>

									<td id="invoice-line-td" style="width:10.6%">
										<span style="font-weight:bold;">
											<xsl:text>Byn. Edilen Kıymet Değeri</xsl:text>
										</span>
									</td>
								</xsl:if>
							</tr>

							<xsl:if test="count(//n1:Invoice/cac:InvoiceLine) &gt;= 1">
								<xsl:for-each select="//n1:Invoice/cac:InvoiceLine">
									<xsl:apply-templates select="."/>
								</xsl:for-each>
							</xsl:if>

							<xsl:if test="count(//n1:Invoice/cac:InvoiceLine) &lt; 1">
								<xsl:choose>
									<xsl:when test="//n1:Invoice/cac:InvoiceLine[1]">
										<xsl:apply-templates
												select="//n1:Invoice/cac:InvoiceLine[1]"/>
									</xsl:when>
									<xsl:otherwise>
										<xsl:apply-templates select="//n1:Invoice"/>
									</xsl:otherwise>
								</xsl:choose>
							</xsl:if>
						</tbody>
					</table>
				</xsl:for-each>


				<table id="budgetContainerTable" table-layout="fixed" width="800px">
					<tbody>
						<tr>
							<xsl:if test="//n1:Invoice/cbc:InvoiceTypeCode='HKSKOMISYONCU' or //n1:Invoice/cbc:InvoiceTypeCode='KOMISYONCU'">
								<td align="left" valign="top" width="300px">
									<table>
										<tbody>
											<xsl:for-each select="n1:Invoice/cac:AllowanceCharge">
												<xsl:if test="cbc:AllowanceChargeReason = 'HKSKOMISYON'">
													<tr align="left" border="0">
														<td align="left" width="200px">
															<span style="font-weight:bold; ">
																<xsl:text>Masraflar:</xsl:text>
															</span>
														</td>

													</tr>
													<tr align="left">
														<td class="lineTableBudgetTd" align="right" width="200px">
															<span style="font-weight:bold; ">
																<xsl:text>Komisyon - %</xsl:text>
															</span>
														</td>
														<td class="lineTableBudgetTd" style="width:81px; " align="right">
															<xsl:for-each
																	select="cbc:Amount">
																<xsl:call-template name="Curr_Type"/>
															</xsl:for-each>
														</td>
														<td class="lineTableBudgetTd" style="width:81px; " align="right">
															<xsl:for-each
																	select="cbc:MultiplierFactorNumeric">
																<xsl:text> %</xsl:text>
																<xsl:call-template name="Curr_Type"/>
															</xsl:for-each>
														</td>
													</tr>
												</xsl:if>
												<xsl:if test="cbc:AllowanceChargeReason = 'HKSKOMISYONKDV' and not(//n1:Invoice/cbc:InvoiceTypeCode='TEVKIFATIADE')">
													<tr align="right">
														<td class="lineTableBudgetTd" align="right" width="200px">
															<span style="font-weight:bold; ">
																<xsl:text>Komisyon KDV - %</xsl:text>
															</span>
														</td>
														<td class="lineTableBudgetTd" style="width:81px; " align="right">
															<xsl:for-each
																	select="cbc:Amount">
																<xsl:call-template name="Curr_Type"/>
															</xsl:for-each>
														</td>
														<td class="lineTableBudgetTd" style="width:81px; " align="right">
															<xsl:for-each
																	select="cbc:MultiplierFactorNumeric">
																<xsl:text> %</xsl:text>
																<xsl:call-template name="Curr_Type"/>
															</xsl:for-each>
														</td>
													</tr>
												</xsl:if>
												<xsl:if test="cbc:AllowanceChargeReason = 'HKSNAVLUN' and not(//n1:Invoice/cbc:InvoiceTypeCode='TEVKIFATIADE')">
													<tr align="right">
														<td class="lineTableBudgetTd" align="right" width="200px">
															<span style="font-weight:bold; ">
																<xsl:text>Navlun - %</xsl:text>
															</span>
														</td>
														<td class="lineTableBudgetTd" style="width:81px; " align="right">
															<xsl:for-each
																	select="cbc:Amount">
																<xsl:call-template name="Curr_Type"/>
															</xsl:for-each>
														</td>
														<td class="lineTableBudgetTd" style="width:81px; " align="right">
															<xsl:for-each
																	select="cbc:MultiplierFactorNumeric">
																<xsl:text> %</xsl:text>
																<xsl:call-template name="Curr_Type"/>
															</xsl:for-each>
														</td>
													</tr>
												</xsl:if>
												<xsl:if test="cbc:AllowanceChargeReason = 'HKSNAVLUNKDV' and not(//n1:Invoice/cbc:InvoiceTypeCode='TEVKIFATIADE')">
													<tr align="right">
														<td class="lineTableBudgetTd" align="right" width="200px">
															<span style="font-weight:bold; ">
																<xsl:text>Navlun KDV - %</xsl:text>
															</span>
														</td>
														<td class="lineTableBudgetTd" style="width:81px; " align="right">
															<xsl:for-each
																	select="cbc:Amount">
																<xsl:call-template name="Curr_Type"/>
															</xsl:for-each>
														</td>
														<td class="lineTableBudgetTd" style="width:81px; " align="right">
															<xsl:for-each
																	select="cbc:MultiplierFactorNumeric">
																<xsl:text> %</xsl:text>
																<xsl:call-template name="Curr_Type"/>
															</xsl:for-each>
														</td>
													</tr>
												</xsl:if>
												<xsl:if test="cbc:AllowanceChargeReason = 'HKSHAMMALIYE' and not(//n1:Invoice/cbc:InvoiceTypeCode='TEVKIFATIADE')">
													<tr align="right">
														<td class="lineTableBudgetTd" align="right" width="200px">
															<span style="font-weight:bold; ">
																<xsl:text>Hammaliye - %</xsl:text>
															</span>
														</td>
														<td class="lineTableBudgetTd" style="width:81px; " align="right">
															<xsl:for-each
																	select="cbc:Amount">
																<xsl:call-template name="Curr_Type"/>
															</xsl:for-each>
														</td>
														<td class="lineTableBudgetTd" style="width:81px; " align="right">
															<xsl:for-each
																	select="cbc:MultiplierFactorNumeric">
																<xsl:text> %</xsl:text>
																<xsl:call-template name="Curr_Type"/>
															</xsl:for-each>
														</td>
													</tr>
												</xsl:if>
												<xsl:if test="cbc:AllowanceChargeReason = 'HKSHAMMALIYEKDV' and not(//n1:Invoice/cbc:InvoiceTypeCode='TEVKIFATIADE')">
													<tr align="right">
														<td class="lineTableBudgetTd" align="right" width="200px">
															<span style="font-weight:bold; ">
																<xsl:text>Hammaliye KDV - %</xsl:text>
															</span>
														</td>
														<td class="lineTableBudgetTd" style="width:81px; " align="right">
															<xsl:for-each
																	select="cbc:Amount">
																<xsl:call-template name="Curr_Type"/>
															</xsl:for-each>
														</td>
														<td class="lineTableBudgetTd" style="width:81px; " align="right">
															<xsl:for-each
																	select="cbc:MultiplierFactorNumeric">
																<xsl:text> %</xsl:text>
																<xsl:call-template name="Curr_Type"/>
															</xsl:for-each>
														</td>
													</tr>
												</xsl:if>
												<xsl:if test="cbc:AllowanceChargeReason = 'HKSNAKLIYE' and not(//n1:Invoice/cbc:InvoiceTypeCode='TEVKIFATIADE')">
													<tr align="right">
														<td class="lineTableBudgetTd" align="right" width="200px">
															<span style="font-weight:bold; ">
																<xsl:text>Nakliye - %</xsl:text>
															</span>
														</td>
														<td class="lineTableBudgetTd" style="width:81px; " align="right">
															<xsl:for-each
																	select="cbc:Amount">
																<xsl:call-template name="Curr_Type"/>
															</xsl:for-each>
														</td>
														<td class="lineTableBudgetTd" style="width:81px; " align="right">
															<xsl:for-each
																	select="cbc:MultiplierFactorNumeric">
																<xsl:text> %</xsl:text>
																<xsl:call-template name="Curr_Type"/>
															</xsl:for-each>
														</td>
													</tr>
												</xsl:if>
												<xsl:if test="cbc:AllowanceChargeReason = 'HKSNAKLIYEKDV' and not(//n1:Invoice/cbc:InvoiceTypeCode='TEVKIFATIADE')">
													<tr align="right">
														<td class="lineTableBudgetTd" align="right" width="200px">
															<span style="font-weight:bold; ">
																<xsl:text>Nakliye KDV - %</xsl:text>
															</span>
														</td>
														<td class="lineTableBudgetTd" style="width:81px; " align="right">
															<xsl:for-each
																	select="cbc:Amount">
																<xsl:call-template name="Curr_Type"/>
															</xsl:for-each>
														</td>
														<td class="lineTableBudgetTd" style="width:81px; " align="right">
															<xsl:for-each
																	select="cbc:MultiplierFactorNumeric">
																<xsl:text> %</xsl:text>
																<xsl:call-template name="Curr_Type"/>
															</xsl:for-each>
														</td>
													</tr>
												</xsl:if>
												<xsl:if test="cbc:AllowanceChargeReason = 'HKSGVTEVKIFAT' and not(//n1:Invoice/cbc:InvoiceTypeCode='TEVKIFATIADE')">
													<tr align="right">
														<td class="lineTableBudgetTd" align="right" width="200px">
															<span style="font-weight:bold; ">
																<xsl:text>G.V. Tevkifat - %</xsl:text>
															</span>
														</td>
														<td class="lineTableBudgetTd" style="width:81px; " align="right">
															<xsl:for-each
																	select="cbc:Amount">
																<xsl:call-template name="Curr_Type"/>
															</xsl:for-each>
														</td>
														<td class="lineTableBudgetTd" style="width:81px; " align="right">
															<xsl:for-each
																	select="cbc:MultiplierFactorNumeric">
																<xsl:text> %</xsl:text>
																<xsl:call-template name="Curr_Type"/>
															</xsl:for-each>
														</td>
													</tr>
												</xsl:if>
												<xsl:if test="cbc:AllowanceChargeReason = 'HKSBAGKURTEVKIFAT' and not(//n1:Invoice/cbc:InvoiceTypeCode='TEVKIFATIADE')">
													<tr align="right">
														<td class="lineTableBudgetTd" align="right" width="200px">
															<span style="font-weight:bold; ">
																<xsl:text>Bağkur Tevkifat - %</xsl:text>
															</span>
														</td>
														<td class="lineTableBudgetTd" style="width:81px; " align="right">
															<xsl:for-each
																	select="cbc:Amount">
																<xsl:call-template name="Curr_Type"/>
															</xsl:for-each>
														</td>
														<td class="lineTableBudgetTd" style="width:81px; " align="right">
															<xsl:for-each
																	select="cbc:MultiplierFactorNumeric">
																<xsl:text> %</xsl:text>
																<xsl:call-template name="Curr_Type"/>
															</xsl:for-each>
														</td>
													</tr>
												</xsl:if>
												<xsl:if test="cbc:AllowanceChargeReason = 'HKSRUSUM' and not(//n1:Invoice/cbc:InvoiceTypeCode='TEVKIFATIADE')">
													<tr align="right">
														<td class="lineTableBudgetTd" align="right" width="200px">
															<span style="font-weight:bold; ">
																<xsl:text>Rüsum - %</xsl:text>
															</span>
														</td>
														<td class="lineTableBudgetTd" style="width:81px; " align="right">
															<xsl:for-each
																	select="cbc:Amount">
																<xsl:call-template name="Curr_Type"/>
															</xsl:for-each>
														</td>
														<td class="lineTableBudgetTd" style="width:81px; " align="right">
															<xsl:for-each
																	select="cbc:MultiplierFactorNumeric">
																<xsl:text> %</xsl:text>
																<xsl:call-template name="Curr_Type"/>
															</xsl:for-each>
														</td>
													</tr>
												</xsl:if>
												<xsl:if test="cbc:AllowanceChargeReason = 'HKSRUSUMKDV' and not(//n1:Invoice/cbc:InvoiceTypeCode='TEVKIFATIADE')">
													<tr align="right">
														<td class="lineTableBudgetTd" align="right" width="200px">
															<span style="font-weight:bold; ">
																<xsl:text>Rüsum KDV - %</xsl:text>
															</span>
														</td>
														<td class="lineTableBudgetTd" style="width:81px; " align="right">
															<xsl:for-each
																	select="cbc:Amount">
																<xsl:call-template name="Curr_Type"/>
															</xsl:for-each>
														</td>
														<td class="lineTableBudgetTd" style="width:81px; " align="right">
															<xsl:for-each
																	select="cbc:MultiplierFactorNumeric">
																<xsl:text> %</xsl:text>
																<xsl:call-template name="Curr_Type"/>
															</xsl:for-each>
														</td>
													</tr>
												</xsl:if>
												<xsl:if test="cbc:AllowanceChargeReason = 'HKSTICBORSASI' and not(//n1:Invoice/cbc:InvoiceTypeCode='TEVKIFATIADE')">
													<tr align="right">
														<td class="lineTableBudgetTd" align="right" width="200px">
															<span style="font-weight:bold; ">
																<xsl:text>Ticaret Borsası - %</xsl:text>
															</span>
														</td>
														<td class="lineTableBudgetTd" style="width:81px; " align="right">
															<xsl:for-each
																	select="cbc:Amount">
																<xsl:call-template name="Curr_Type"/>
															</xsl:for-each>
														</td>
														<td class="lineTableBudgetTd" style="width:81px; " align="right">
															<xsl:for-each
																	select="cbc:MultiplierFactorNumeric">
																<xsl:text> %</xsl:text>
																<xsl:call-template name="Curr_Type"/>
															</xsl:for-each>
														</td>
													</tr>
												</xsl:if>
												<xsl:if test="cbc:AllowanceChargeReason = 'HKSTICBORSASIKDV' and not(//n1:Invoice/cbc:InvoiceTypeCode='TEVKIFATIADE')">
													<tr align="right">
														<td class="lineTableBudgetTd" align="right" width="200px">
															<span style="font-weight:bold; ">
																<xsl:text>Ticaret Borsası KDV - %</xsl:text>
															</span>
														</td>
														<td class="lineTableBudgetTd" style="width:81px; " align="right">
															<xsl:for-each
																	select="cbc:Amount">
																<xsl:call-template name="Curr_Type"/>
															</xsl:for-each>
														</td>
														<td class="lineTableBudgetTd" style="width:81px; " align="right">
															<xsl:for-each
																	select="cbc:MultiplierFactorNumeric">
																<xsl:text> %</xsl:text>
																<xsl:call-template name="Curr_Type"/>
															</xsl:for-each>
														</td>
													</tr>
												</xsl:if>
												<xsl:if test="cbc:AllowanceChargeReason = 'HKSMILLISAVUNMAFON' and not(//n1:Invoice/cbc:InvoiceTypeCode='TEVKIFATIADE')">
													<tr align="right">
														<td class="lineTableBudgetTd" align="right" width="200px">
															<span style="font-weight:bold; ">
																<xsl:text>Milli Savunma Fon - %</xsl:text>
															</span>
														</td>
														<td class="lineTableBudgetTd" style="width:81px; " align="right">
															<xsl:for-each
																	select="cbc:Amount">
																<xsl:call-template name="Curr_Type"/>
															</xsl:for-each>
														</td>
														<td class="lineTableBudgetTd" style="width:81px; " align="right">
															<xsl:for-each
																	select="cbc:MultiplierFactorNumeric">
																<xsl:text> %</xsl:text>
																<xsl:call-template name="Curr_Type"/>
															</xsl:for-each>
														</td>
													</tr>
												</xsl:if>
												<xsl:if test="cbc:AllowanceChargeReason = 'HKSMSFONKDV' and not(//n1:Invoice/cbc:InvoiceTypeCode='TEVKIFATIADE')">
													<tr align="right">
														<td class="lineTableBudgetTd" align="right" width="200px">
															<span style="font-weight:bold; ">
																<xsl:text>Milli Savunma Fon KDV - %</xsl:text>
															</span>
														</td>
														<td class="lineTableBudgetTd" style="width:81px; " align="right">
															<xsl:for-each
																	select="cbc:Amount">
																<xsl:call-template name="Curr_Type"/>
															</xsl:for-each>
														</td>
														<td class="lineTableBudgetTd" style="width:81px; " align="right">
															<xsl:for-each
																	select="cbc:MultiplierFactorNumeric">
																<xsl:text> %</xsl:text>
																<xsl:call-template name="Curr_Type"/>
															</xsl:for-each>
														</td>
													</tr>
												</xsl:if>
												<xsl:if test="cbc:AllowanceChargeReason = 'HKSDIGERMASRAFLAR' and not(//n1:Invoice/cbc:InvoiceTypeCode='TEVKIFATIADE')">
													<tr align="right">
														<td class="lineTableBudgetTd" align="right" width="200px">
															<span style="font-weight:bold; ">
																<xsl:text>Diğer Masraflar - %</xsl:text>
															</span>
														</td>
														<td class="lineTableBudgetTd" style="width:81px; " align="right">
															<xsl:for-each
																	select="cbc:Amount">
																<xsl:call-template name="Curr_Type"/>
															</xsl:for-each>
														</td>
														<td class="lineTableBudgetTd" style="width:81px; " align="right">
															<xsl:for-each
																	select="cbc:MultiplierFactorNumeric">
																<xsl:text> %</xsl:text>
																<xsl:call-template name="Curr_Type"/>
															</xsl:for-each>
														</td>
													</tr>
												</xsl:if>
												<xsl:if test="cbc:AllowanceChargeReason = 'HKSDIGERKDV' and not(//n1:Invoice/cbc:InvoiceTypeCode='TEVKIFATIADE')">
													<tr align="right">
														<td class="lineTableBudgetTd" align="right" width="200px">
															<span style="font-weight:bold; ">
																<xsl:text>Diğer KDV - %</xsl:text>
															</span>
														</td>
														<td class="lineTableBudgetTd" style="width:81px; " align="right">
															<xsl:for-each
																	select="cbc:Amount">
																<xsl:call-template name="Curr_Type"/>
															</xsl:for-each>
														</td>
														<td class="lineTableBudgetTd" style="width:81px; " align="right">
															<xsl:for-each
																	select="cbc:MultiplierFactorNumeric">
																<xsl:text> %</xsl:text>
																<xsl:call-template name="Curr_Type"/>
															</xsl:for-each>
														</td>
													</tr>
												</xsl:if>
											</xsl:for-each>

										</tbody>
									</table>
								</td>
							</xsl:if>
							<td align="right" valign="top">
								<table>
									<tbody>
										<xsl:if test="not($varfaturatipi='SGK' and $varoptik='medula')">
											<tr align="right">
												<td/>
												<xsl:if test="not(//n1:Invoice/cbc:InvoiceTypeCode='TEVKIFATIADE')">
												<td class="lineTableBudgetTd" align="right" width="200px">
													<span style="font-weight:bold; ">
														<xsl:text>Mal Hizmet Toplam Tutarı</xsl:text>
													</span>
												</td>
												</xsl:if>

												<xsl:if test="//n1:Invoice/cbc:InvoiceTypeCode='TEVKIFATIADE'">
												<td class="lineTableBudgetTd" align="right" width="200px">
													<span style="font-weight:bold; ">
														<xsl:text>İadeye Konu İşlem Bedeli Tutarı</xsl:text>
													</span>
												</td>
												</xsl:if>
												<td class="lineTableBudgetTd" style="width:81px; " align="right">
													<xsl:for-each select="n1:Invoice/cac:LegalMonetaryTotal/cbc:LineExtensionAmount">
														<xsl:call-template name="Curr_Type"/>
													</xsl:for-each>
												</td>
											</tr>
										</xsl:if>
										<xsl:for-each select="n1:Invoice/cac:TaxTotal/cac:TaxSubtotal">
											<xsl:if test="cac:TaxCategory/cac:TaxScheme/cbc:TaxTypeCode = '4171'">
												<tr align="right">
													<td/>
													<td class="lineTableBudgetTd" align="right" width="200px">
														<span style="font-weight:bold; ">
															<xsl:text>Teslim Bedeli</xsl:text>
														</span>
													</td>
													<td class="lineTableBudgetTd" style="width:81px; " align="right">
														<xsl:for-each select="//n1:Invoice/cac:LegalMonetaryTotal/cbc:LineExtensionAmount">
															<xsl:call-template name="Curr_Type"/>
														</xsl:for-each>
													</td>
												</tr>
											</xsl:if>
										</xsl:for-each>
										<xsl:if test="not($varfaturatipi='SGK')">
											<tr align="right">
												<td/>
												<xsl:choose>
													<xsl:when
															test="//n1:Invoice/cac:AllowanceCharge/cbc:ChargeIndicator='true'">
														<td class="lineTableBudgetTd" align="right" width="200px">
															<span style="font-weight:bold; ">
																<xsl:text>Toplam Arttırım - </xsl:text>
																<xsl:for-each
																		select="n1:Invoice/cac:AllowanceCharge/cbc:AllowanceChargeReason">
																	<xsl:apply-templates/>
																</xsl:for-each>
															</span>
														</td>
													</xsl:when>
													<xsl:otherwise>
														<td class="lineTableBudgetTd" align="right" width="200px">
															<span style="font-weight:bold; ">
																<xsl:if test="not($varoptik='medikal')">
																	<xsl:text>Toplam İskonto</xsl:text>
																</xsl:if>
																<xsl:if test="$varoptik='medikal'">
																	<xsl:text>Katılım Payı</xsl:text>
																</xsl:if>
															</span>
														</td>
													</xsl:otherwise>
												</xsl:choose>
												<td class="lineTableBudgetTd" style="width:81px; " align="right">
													<xsl:if test="$varoptik='medikal' and not($varisitmekatilimpayi='')" >
														<xsl:value-of select="format-number(number($varisitmekatilimpayi), '###.##0,00', 'european')" />
														<xsl:text> TL</xsl:text>
													</xsl:if>
													<xsl:if test="not($varoptik='medikal' and not($varisitmekatilimpayi=''))" >
														<xsl:for-each select="n1:Invoice/cac:LegalMonetaryTotal/cbc:AllowanceTotalAmount">
															<xsl:call-template name="Curr_Type"/>
														</xsl:for-each>
													</xsl:if>
												</td>
											</tr>
										</xsl:if>

										<xsl:if test="$varfaturatipi='SGK' and $varoptik='cezaeviEczanem'">
											<tr align="right">
												<td/>
												<td class="lineTableBudgetTd" align="right" width="200px">
													<span style="font-weight:bold; ">
														<xsl:text>Toplam İskonto</xsl:text>
													</span>
												</td>
												<td class="lineTableBudgetTd" style="width:81px; " align="right">
													<span>
														<xsl:value-of select="format-number(number($variskonto), '###.##0,00', 'european')" />
														<xsl:text> TL</xsl:text>
													</span>
												</td>
											</tr>
											<tr align="right">
												<td/>
												<td class="lineTableBudgetTd" align="right" width="200px">
													<span style="font-weight:bold; ">
														<xsl:text>İlaç Farkı</xsl:text>
													</span>
												</td>
												<td class="lineTableBudgetTd" style="width:81px; " align="right">
													<span>
														<xsl:value-of select="format-number(number($varilacfarki), '###.##0,00', 'european')" />
														<xsl:text> TL</xsl:text>
													</span>
												</td>
											</tr>
										</xsl:if>
										<xsl:if test="$varfaturatipi='SGK' and $varoptik='optik'">
											<tr align="right">
												<td/>
												<td class="lineTableBudgetTd" align="right" width="200px">
													<span style="font-weight:bold; ">
														<xsl:text>Toplam Katılım Payı</xsl:text>
													</span>
												</td>
												<td class="lineTableBudgetTd" style="width:81px; " align="right">
													<span>
														<xsl:value-of select="format-number(number($varkatilimpayi), '###.##0,00', 'european')" />
														<xsl:text> TL</xsl:text>
													</span>
												</td>
											</tr>
										</xsl:if>
										<xsl:if test="$varfaturatipi='SGK' and $varoptik='medula'">
											<!--TEBEOS Cezaevi faturası için sgk şeklinde bir tasarım istermiştir ona göre düzenleme yapılmıştır.
                                                Resources altına oluşturdukları xml atılacaktır. Değişiklik yaparken o xmle de görede kontrol sağlanmalıdır.-->
											<xsl:if test="not($varpsf='undefined' or $varpsf='' or $varfaturatype='CETAS')">
												<tr align="right">
													<td/>
													<td class="lineTableBudgetTd" align="right" width="200px">
														<span style="font-weight:bold; ">
															<xsl:value-of select="$varreceteadedi" /> Adet Reçete PSF Toplamı
														</span>
													</td>
													<td class="lineTableBudgetTd" style="width:81px; " align="right">
														<span>
															<xsl:value-of select="format-number(number($varpsf), '###.##0,00', 'european')" />
															<xsl:text> TL</xsl:text>
														</span>
													</td>
												</tr>
											</xsl:if>
											<!--TEBEOS Cezaevi faturası için sgk şeklinde bir tasarım istermiştir ona göre düzenleme yapılmıştır.
												Resources altına oluşturdukları xml atılacaktır. Değişiklik yaparken o xmle de görede kontrol sağlanmalıdır.-->
											<xsl:if test="not($varpsf='undefined' or $varpsf='' or $varfaturatype='CETAS')">
												<tr align="right">
													<td/>
													<td class="lineTableBudgetTd" align="right" width="200px">
														<span style="font-weight:bold; ">
															<xsl:text>Kamu Kurum İskontosu</xsl:text>
														</span>
													</td>
													<td class="lineTableBudgetTd" style="width:81px; " align="right">
														<span>
															<xsl:value-of select="format-number((number($varpsf)- number($vartutar)), '###.##0,00', 'european')" />
															<xsl:text> TL</xsl:text>
														</span>
													</td>
												</tr>
											</xsl:if>
											<!--TEBEOS Cezaevi faturası için sgk şeklinde bir tasarım istermiştir ona göre düzenleme yapılmıştır.
                                                Resources altına oluşturdukları xml atılacaktır. Değişiklik yaparken o xmle de görede kontrol sağlanmalıdır.-->
											<xsl:if test="not($varfaturatype='CETAS')">
												<tr align="right">
													<td/>
													<td class="lineTableBudgetTd" align="right" width="200px">
														<span style="font-weight:bold; ">
															<xsl:value-of select="$varreceteadedi"/> Adet Reçete Kamu Fiyatı Toplamı
														</span>
													</td>
													<td class="lineTableBudgetTd" style="width:81px; " align="right">
														<span>
															<xsl:for-each select="n1:Invoice/cac:LegalMonetaryTotal/cbc:LineExtensionAmount">
																<xsl:call-template name="Curr_Type"/>
															</xsl:for-each>
														</span>
													</td>
												</tr>
											</xsl:if>
											<tr align="right">
												<td/>
												<td class="lineTableBudgetTd" align="right" width="200px">
													<span style="font-weight:bold; ">
														<xsl:text>Eczane İskontosu</xsl:text>
													</span>
												</td>
												<td class="lineTableBudgetTd" style="width:81px; " align="right">
													<span>
														<xsl:for-each select="n1:Invoice/cac:LegalMonetaryTotal/cbc:AllowanceTotalAmount">
															<xsl:call-template name="Curr_Type"/>
														</xsl:for-each>
													</span>
												</td>
											</tr>
											<!--TEBEOS Cezaevi faturası için sgk şeklinde bir tasarım istermiştir ona göre düzenleme yapılmıştır.
												Resources altına oluşturdukları xml atılacaktır. Değişiklik yaparken o xmle de görede kontrol sağlanmalıdır.-->
											<xsl:if test="not($varfaturatype='CETAS')">
												<tr align="right">
													<td/>
													<td class="lineTableBudgetTd" align="right" width="200px">
														<span style="font-weight:bold; ">
															<xsl:text>Hasta Katılım Payı(%10 - %20)</xsl:text>
														</span>
													</td>
													<td class="lineTableBudgetTd" style="width:81px; " align="right">
														<span>
															<xsl:value-of select="format-number(number($varkatilimpayi), '###.##0,00', 'european')"/>
															<xsl:text> TL</xsl:text>
														</span>
													</td>
												</tr>
											</xsl:if>
											<!--TEBEOS Cezaevi faturası için sgk şeklinde bir tasarım istermiştir ona göre düzenleme yapılmıştır.
												Resources altına oluşturdukları xml atılacaktır. Değişiklik yaparken o xmle de görede kontrol sağlanmalıdır.-->
											<xsl:if test="not($varfaturatype='CETAS')">
												<tr align="right">
													<td/>
													<td class="lineTableBudgetTd" width="210px" align="right">
														<span style="font-weight:bold; ">
															<xsl:text>Vergiler Dahil Reçete Toplam Tutarı</xsl:text>
														</span>
													</td>
													<td class="lineTableBudgetTd" style="width:82px; " align="right">
														<span>
															<xsl:value-of select="format-number((number($vartutar) -(number($variskonto) + number($varkatilimpayi))), '###.##0,00', 'european')"/>
															<xsl:text> TL</xsl:text>
														</span>
													</td>
												</tr>
											</xsl:if>
											<!--TEBEOS Cezaevi faturası için sgk şeklinde bir tasarım istermiştir ona göre düzenleme yapılmıştır.
												Resources altına oluşturdukları xml atılacaktır. Değişiklik yaparken o xmle de görede kontrol sağlanmalıdır.-->
											<xsl:if test="not($varfaturatype='CETAS')">
												<tr align="right">
													<td/>
													<td class="lineTableBudgetTd" width="210px" align="right">
														<span style="font-weight:bold; ">
															<xsl:text>Vergiler Hariç Reçete Toplam Tutarı</xsl:text>
														</span>
													</td>
													<td class="lineTableBudgetTd" style="width:82px; " align="right">
														<span>
															<xsl:value-of select="format-number((number($vartutar) -(number($variskonto) + number($varkatilimpayi) + number($varkdv8) + number($varkdv10) + number($varkdv18) + number($varkdv20))), '###.##0,00', 'european')"/>
															<xsl:text> TL</xsl:text>
														</span>
													</td>
												</tr>
											</xsl:if>
											<xsl:if test="not($varkdv8='undefined' or $varkdv8='')">
												<tr align="right">
													<td/>
													<td class="lineTableBudgetTd" align="right" width="200px">
														<span style="font-weight:bold; ">
															<xsl:text>KDV (%8)</xsl:text>
														</span>
													</td>
													<td class="lineTableBudgetTd" style="width:81px; " align="right">
														<span>
															<xsl:value-of select="format-number(number($varkdv8), '###.##0,00', 'european')" />
															<xsl:text> TL</xsl:text>
														</span>
													</td>
												</tr>
											</xsl:if>
											<xsl:if test="not($varkdv10='undefined' or $varkdv10='')">
												<tr align="right">
													<td/>
													<td class="lineTableBudgetTd" align="right" width="200px">
														<span style="font-weight:bold; ">
															<xsl:text>KDV (%10)</xsl:text>
														</span>
													</td>
													<td class="lineTableBudgetTd" style="width:81px; " align="right">
														<span>
															<xsl:value-of select="format-number(number($varkdv10), '###.##0,00', 'european')" />
															<xsl:text> TL</xsl:text>
														</span>
													</td>
												</tr>
											</xsl:if>
											<xsl:if test="not($varkdv18='undefined' or $varkdv18='')">
												<tr align="right">
													<td/>
													<td class="lineTableBudgetTd" align="right" width="200px">
														<span style="font-weight:bold; ">
															<xsl:text>KDV (%18)</xsl:text>
														</span>
													</td>
													<td class="lineTableBudgetTd" style="width:81px; " align="right">
														<span>
															<xsl:value-of select="format-number(number($varkdv18), '###.##0,00', 'european')" />
															<xsl:text> TL</xsl:text>
														</span>
													</td>
												</tr>
											</xsl:if>
											<xsl:if test="not($varkdv20='undefined' or $varkdv20='')">
												<tr align="right">
													<td/>
													<td class="lineTableBudgetTd" align="right" width="200px">
														<span style="font-weight:bold; ">
															<xsl:text>KDV (%20)</xsl:text>
														</span>
													</td>
													<td class="lineTableBudgetTd" style="width:81px; " align="right">
														<span>
															<xsl:value-of select="format-number(number($varkdv20), '###.##0,00', 'european')" />
															<xsl:text> TL</xsl:text>
														</span>
													</td>
												</tr>
											</xsl:if>
											<!--TEBEOS Cezaevi faturası için sgk şeklinde bir tasarım istermiştir ona göre düzenleme yapılmıştır.
												Resources altına oluşturdukları xml atılacaktır. Değişiklik yaparken o xmle de görede kontrol sağlanmalıdır.-->
											<xsl:if test="not($varfaturatype='CETAS')">
												<tr align="right">
													<td/>
													<td class="lineTableBudgetTd" width="220px" align="right">
														<span style="font-weight:bold; ">
															<xsl:text>Vergiler Dahil Reçete Toplam Tutarı</xsl:text>
														</span>
													</td>
													<td class="lineTableBudgetTd" style="width:82px; " align="right">
														<span>
															<xsl:value-of select="format-number((number($vartutar) -(number($variskonto) + number($varkatilimpayi))), '###.##0,00', 'european')"/>
															<xsl:text> TL</xsl:text>
														</span>
													</td>
												</tr>
											</xsl:if>
											<tr align="right">
												<td/>
												<td class="lineTableBudgetTd" align="right" width="210px">
													<span style="font-weight:bold; ">
														<xsl:choose>
															<!--TEBEOS Cezaevi faturası için sgk şeklinde bir tasarım istermiştir ona göre düzenleme yapılmıştır.
                                                                Resources altına oluşturdukları xml atılacaktır. Değişiklik yaparken o xmle de görede kontrol sağlanmalıdır.-->
															<xsl:when test="$varfaturatype='CETAS'">
																<xsl:text>Eczane Hizmet Bedeli KDV(%18) Hariç Tutarı</xsl:text>
															</xsl:when>
															<xsl:otherwise>
																<xsl:text>Eczane Hizmet Bedeli KDV Hariç Tutarı</xsl:text>
															</xsl:otherwise>
														</xsl:choose>
													</span>
												</td>
												<td class="lineTableBudgetTd" style="width:81px; " align="right">
													<xsl:choose>
														<!--TEBEOS Cezaevi faturası için sgk şeklinde bir tasarım istermiştir ona göre düzenleme yapılmıştır.
                                                            Resources altına oluşturdukları xml atılacaktır. Değişiklik yaparken o xmle de görede kontrol sağlanmalıdır.-->
														<xsl:when test="$varfaturatype='CETAS'">
															<xsl:value-of select="format-number((number($vareczanehizmetbedeli) - number($vareczanekdv18)), '###.##0,00', 'european')" />
														</xsl:when>
														<xsl:otherwise>
															<xsl:value-of select="format-number((number($vareczanehizmetbedeli) - number($vareczanekdv18) - number($vareczanekdv20)), '###.##0,00', 'european')" />
														</xsl:otherwise>
													</xsl:choose>
													<xsl:text> TL</xsl:text>
												</td>
											</tr>
											<!--TEBEOS Cezaevi faturası için sgk şeklinde bir tasarım istermiştir ona göre düzenleme yapılmıştır.
											Resources altına oluşturdukları xml atılacaktır. Değişiklik yaparken o xmle de görede kontrol sağlanmalıdır.-->
											<xsl:if test="$varfaturatype='CETAS'">
												<tr align="right">
													<td/>
													<td class="lineTableBudgetTd" align="right" width="210px">
														<span style="font-weight:bold; ">
															<xsl:text>Eczane Hizmet Bedeli KDV(%20) Hariç Tutarı</xsl:text>
														</span>
													</td>
													<td class="lineTableBudgetTd" style="width:81px; " align="right">
														<!--TEBEOS Cezaevi faturası için sgk şeklinde bir tasarım istermiştir ona göre düzenleme yapılmıştır.
                                                            Resources altına oluşturdukları xml atılacaktır. Değişiklik yaparken o xmle de görede kontrol sağlanmalıdır.-->
														<xsl:value-of select="format-number((number($vareczanehizmetbedeli20) - number($vareczanekdv20)), '###.##0,00', 'european')"/>
														<xsl:text> TL</xsl:text>
													</td>
												</tr>
											</xsl:if>

											<tr align="right">
												<td/>
												<td class="lineTableBudgetTd" align="right" width="200px">
													<span style="font-weight:bold; ">
														<xsl:choose>
															<!--TEBEOS Cezaevi faturası için sgk şeklinde bir tasarım istermiştir ona göre düzenleme yapılmıştır.
																Resources altına oluşturdukları xml atılacaktır. Değişiklik yaparken o xmle de görede kontrol sağlanmalıdır.-->
															<xsl:when test="$varfaturatype='CETAS'">
																<xsl:text>Eczane Hizmet Bedeli KDV (%18)</xsl:text>
															</xsl:when>
															<xsl:otherwise>
																<xsl:text>KDV (%18)</xsl:text>
															</xsl:otherwise>
														</xsl:choose>
													</span>
												</td>
												<td class="lineTableBudgetTd" style="width:81px; " align="right">
													<xsl:value-of select="format-number(number($vareczanekdv18), '###.##0,00', 'european')" />
													<xsl:text> TL</xsl:text>
												</td>
											</tr>
											<tr align="right">
												<td/>
												<td class="lineTableBudgetTd" align="right" width="200px">
													<span style="font-weight:bold; ">
														<xsl:choose>
															<!--TEBEOS Cezaevi faturası için sgk şeklinde bir tasarım istermiştir ona göre düzenleme yapılmıştır.
																Resources altına oluşturdukları xml atılacaktır. Değişiklik yaparken o xmle de görede kontrol sağlanmalıdır.-->
															<xsl:when test="$varfaturatype='CETAS'">
																<xsl:text>Eczane Hizmet Bedeli KDV (%20)</xsl:text>
															</xsl:when>
															<xsl:otherwise>
																<xsl:text>KDV (%20)</xsl:text>
															</xsl:otherwise>
														</xsl:choose>
													</span>
												</td>
												<td class="lineTableBudgetTd" style="width:81px; " align="right">
													<xsl:value-of select="format-number(number($vareczanekdv20), '###.##0,00', 'european')" />
													<xsl:text> TL</xsl:text>
												</td>
											</tr>

											<tr align="right">
												<td/>
												<td class="lineTableBudgetTd" align="right" width="210px">
													<span style="font-weight:bold; ">
														<xsl:choose>
															<!--TEBEOS Cezaevi faturası için sgk şeklinde bir tasarım istermiştir ona göre düzenleme yapılmıştır.
																Resources altına oluşturdukları xml atılacaktır. Değişiklik yaparken o xmle de görede kontrol sağlanmalıdır.-->
															<xsl:when test="$varfaturatype='CETAS'">
																<xsl:text>Eczane Hizmet Bedeli KDV(%18) Dahil Tutarı</xsl:text>
															</xsl:when>
															<xsl:otherwise>
																<xsl:text>Eczane Hizmet Bedeli KDV Dahil Tutarı</xsl:text>
															</xsl:otherwise>
														</xsl:choose>
													</span>
												</td>
												<td class="lineTableBudgetTd" style="width:81px; " align="right">
													<xsl:value-of select="format-number(number($vareczanehizmetbedeli), '###.##0,00', 'european')" />
													<xsl:text> TL</xsl:text>
												</td>
											</tr>

											<!--TEBEOS Cezaevi faturası için sgk şeklinde bir tasarım istermiştir ona göre düzenleme yapılmıştır.
											Resources altına oluşturdukları xml atılacaktır. Değişiklik yaparken o xmle de görede kontrol sağlanmalıdır.-->
											<xsl:if test="$varfaturatype='CETAS'">
												<tr align="right">
													<td/>
													<td class="lineTableBudgetTd" align="right" width="210px">
														<span style="font-weight:bold; ">
															<xsl:text>Eczane Hizmet Bedeli KDV(%20) Dahil Tutarı</xsl:text>
														</span>
													</td>
													<td class="lineTableBudgetTd" style="width:81px; " align="right">
														<xsl:value-of select="format-number(number($vareczanehizmetbedeli20), '###.##0,00', 'european')"/>
														<xsl:text> TL</xsl:text>
													</td>
												</tr>
											</xsl:if>
										</xsl:if>

										<!-- KDV_TAXABLEAMOUNT_REF -->
										<!-- EXCHANGERATE_REF -->

										<xsl:if test="$varfaturatipi='SGK' and $varoptik='medikalIcmal'">
											<xsl:if test="string-length($varkatilimpayi)>0 and not($varkatilimpayi=0)">
												<tr align="right">
													<td/>
													<td class="lineTableBudgetTd" width="211px" align="right">
														<span style="font-weight:bold; ">
															<xsl:text>Katılım Payı</xsl:text>
														</span>
													</td>
													<td class="lineTableBudgetTd" style="width:82px; " align="right">
														<xsl:value-of select="format-number(number($varkatilimpayi), '###.##0,00', 'european')"/>
														<xsl:text> TL</xsl:text>
													</td>
												</tr>
											</xsl:if>
										</xsl:if>

										<xsl:if test="not(//n1:Invoice/cbc:InvoiceTypeCode='TEVKIFATIADE')">
											<xsl:if test="not($varfaturatipi='SGK' and $varoptik='medula')">
												<xsl:for-each select="n1:Invoice/cac:TaxTotal/cac:TaxSubtotal">
													<tr align="right">
														<td/>
														<td class="lineTableBudgetTd" width="211px" align="right">
															<span style="font-weight:bold; ">
																<xsl:text>Hesaplanan </xsl:text>
																<xsl:value-of
																		select="cac:TaxCategory/cac:TaxScheme/cbc:Name"/>
																<xsl:if test="../../cbc:InvoiceTypeCode!='OZELMATRAH'">
																	<xsl:text>(%</xsl:text>
																	<xsl:value-of select="cbc:Percent"/>
																	<xsl:text>)</xsl:text>
																</xsl:if>
															</span>
														</td>
														<td class="lineTableBudgetTd" style="width:82px; "
															align="right">
															<xsl:for-each select="cac:TaxCategory/cac:TaxScheme">
																<xsl:text> </xsl:text>
																<xsl:value-of
																		select="format-number(../../cbc:TaxAmount, '###.##0,00', 'european')"/>
																<xsl:if test="../../cbc:TaxAmount/@currencyID">
																	<xsl:text> </xsl:text>
																	<xsl:if test="../../cbc:TaxAmount/@currencyID = 'TRL' or ../../cbc:TaxAmount/@currencyID = 'TRY'">
																		<xsl:text>TL</xsl:text>
																	</xsl:if>
																	<xsl:if test="../../cbc:TaxAmount/@currencyID != 'TRL' and ../../cbc:TaxAmount/@currencyID != 'TRY'">
																		<xsl:value-of
																				select="../../cbc:TaxAmount/@currencyID"/>
																	</xsl:if>
																</xsl:if>
															</xsl:for-each>
														</td>
													</tr>
												</xsl:for-each>
											</xsl:if>
										</xsl:if>
										<xsl:if test="(//n1:Invoice/cbc:InvoiceTypeCode='TEVKIFATIADE')">
<!--											<xsl:for-each select="n1:Invoice/cac:TaxTotal/cac:TaxSubtotal">-->
												<tr align="right">
													<td/>
													<td class="lineTableBudgetTd" width="211px" align="right">
														<span style="font-weight:bold; ">
																<xsl:text>İadeye Konu KDV </xsl:text>
														</span>
													</td>
													<td class="lineTableBudgetTd" style="width:82px; " align="right">
														<xsl:text> </xsl:text>
														<xsl:value-of
																select="format-number(sum(//n1:Invoice/cac:TaxTotal/cac:TaxSubtotal[cac:TaxCategory/cac:TaxScheme/cbc:TaxTypeCode=0015]/cbc:TaxAmount), '###.##0,00', 'european')"/>
														<xsl:if test="n1:Invoice/cac:TaxTotal/cac:TaxSubtotal/cbc:TaxAmount/@currencyID">
															<xsl:text> </xsl:text>
															<xsl:if test="n1:Invoice/cac:TaxTotal/cac:TaxSubtotal/cbc:TaxAmount/@currencyID = 'TRL' or n1:Invoice/cac:TaxTotal/cac:TaxSubtotal/cbc:TaxAmount/@currencyID = 'TRY'">
																<xsl:text>TL</xsl:text>
															</xsl:if>
															<xsl:if test="n1:Invoice/cac:TaxTotal/cac:TaxSubtotal/cbc:TaxAmount/@currencyID != 'TRL' and n1:Invoice/cac:TaxTotal/cac:TaxSubtotal/cbc:TaxAmount/@currencyID != 'TRY'">
																<xsl:value-of
																		select="n1:Invoice/cac:TaxTotal/cac:TaxSubtotal/cbc:TaxAmount/@currencyID"/>
															</xsl:if>
														</xsl:if>
													</td>
												</tr>
<!--											</xsl:for-each>-->
										</xsl:if>
										<xsl:for-each select="n1:Invoice/cac:TaxTotal/cac:TaxSubtotal">
											<xsl:if test="cac:TaxCategory/cac:TaxScheme/cbc:TaxTypeCode = '4171'">
												<tr align="right">
													<td/>
													<td class="lineTableBudgetTd" align="right" width="200px">
														<span style="font-weight:bold; ">
															<xsl:text>KDV Matrahı</xsl:text>
														</span>
													</td>
													<td class="lineTableBudgetTd" style="width:81px; " align="right">
														<xsl:value-of
																select="format-number(sum(//n1:Invoice/cac:TaxTotal/cac:TaxSubtotal[cac:TaxCategory/cac:TaxScheme/cbc:TaxTypeCode=0015]/cbc:TaxableAmount), '###.##0,00', 'european')"/>
														<xsl:if
																test="//n1:Invoice/cac:LegalMonetaryTotal/cbc:TaxInclusiveAmount/@currencyID">
															<xsl:text> </xsl:text>
															<xsl:if
																	test="//n1:Invoice/cac:LegalMonetaryTotal/cbc:TaxInclusiveAmount/@currencyID = 'TRL' or //n1:Invoice/cac:LegalMonetaryTotal/cbc:TaxInclusiveAmount/@currencyID = 'TRY'">
																<xsl:text>TL</xsl:text>
															</xsl:if>
															<xsl:if
																	test="//n1:Invoice/cac:LegalMonetaryTotal/cbc:TaxInclusiveAmount/@currencyID != 'TRL' and //n1:Invoice/cac:LegalMonetaryTotal/cbc:TaxInclusiveAmount/@currencyID != 'TRY'">
																<xsl:value-of
																		select="//n1:Invoice/cac:LegalMonetaryTotal/cbc:TaxInclusiveAmount/@currencyID"
																/>
															</xsl:if>
														</xsl:if>
													</td>
												</tr>
												<tr align="right">
													<td/>
													<td class="lineTableBudgetTd" align="right" width="200px">
														<span style="font-weight:bold; ">
															<xsl:text>Tevkifat Dahil Toplam Tutar</xsl:text>
														</span>
													</td>
													<td class="lineTableBudgetTd" style="width:81px; " align="right">
														<xsl:for-each select="//n1:Invoice/cac:LegalMonetaryTotal/cbc:TaxInclusiveAmount">
															<xsl:call-template name="Curr_Type"/>
														</xsl:for-each>
													</td>
												</tr>
												<tr align="right">
													<td/>
													<td class="lineTableBudgetTd" align="right" width="200px">
														<span style="font-weight:bold; ">
															<xsl:text>Tevkifat Hariç Toplam Tutar</xsl:text>
														</span>
													</td>
													<td class="lineTableBudgetTd" style="width:81px; " align="right">
														<xsl:for-each select="//n1:Invoice/cac:LegalMonetaryTotal/cbc:PayableAmount">
															<xsl:call-template name="Curr_Type"/>
														</xsl:for-each>
													</td>
												</tr>
											</xsl:if>
										</xsl:for-each>
										<xsl:for-each select="n1:Invoice/cac:WithholdingTaxTotal/cac:TaxSubtotal">
											<tr align="right">
												<td/>
												<td class="lineTableBudgetTd" width="211px" align="right">
													<span style="font-weight:bold; ">
														<xsl:text>Hesaplanan KDV Tevkifat</xsl:text>
														<xsl:text>(%</xsl:text>
														<xsl:value-of select="cbc:Percent"/>
														<xsl:text>)</xsl:text>
													</span>
												</td>
												<td class="lineTableBudgetTd" style="width:82px; " align="right">
													<xsl:for-each select="cac:TaxCategory/cac:TaxScheme">
														<xsl:text> </xsl:text>
														<xsl:value-of
																select="format-number(../../cbc:TaxAmount, '###.##0,00', 'european')"/>
														<xsl:if test="../../cbc:TaxAmount/@currencyID">
															<xsl:text> </xsl:text>
															<xsl:if test="../../cbc:TaxAmount/@currencyID = 'TRL' or ../../cbc:TaxAmount/@currencyID = 'TRY'">
																<xsl:text>TL</xsl:text>
															</xsl:if>
															<xsl:if test="../../cbc:TaxAmount/@currencyID != 'TRL' and ../../cbc:TaxAmount/@currencyID != 'TRY'">
																<xsl:value-of select="../../cbc:TaxAmount/@currencyID"/>
															</xsl:if>
														</xsl:if>
													</xsl:for-each>
												</td>
											</tr>
										</xsl:for-each>
										<xsl:if test="sum(n1:Invoice/cac:TaxTotal/cac:TaxSubtotal[cac:TaxCategory/cac:TaxScheme/cbc:TaxTypeCode=9015]/cbc:TaxableAmount)>0">
											<tr align="right">
												<td/>
												<td class="lineTableBudgetTd" width="211px" align="right">
													<span style="font-weight:bold; ">
														<xsl:text>Tevkifata Tabi İşlem Tutarı</xsl:text>
													</span>
												</td>
												<td class="lineTableBudgetTd" style="width:82px; " align="right">
													<xsl:value-of
															select="format-number(sum(n1:Invoice/cac:InvoiceLine[cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cac:TaxScheme/cbc:TaxTypeCode=9015]/cbc:LineExtensionAmount), '###.##0,00', 'european')"/>
													<xsl:if test="n1:Invoice/cbc:DocumentCurrencyCode = 'TRL'">
														<xsl:text>TL</xsl:text>
													</xsl:if>
													<xsl:if test="n1:Invoice/cbc:DocumentCurrencyCode != 'TRL'">
														<xsl:value-of select="n1:Invoice/cbc:DocumentCurrencyCode"/>
													</xsl:if>
												</td>
											</tr>
											<tr align="right">
												<td/>
												<td class="lineTableBudgetTd" width="211px" align="right">
													<span style="font-weight:bold; ">
														<xsl:text>Tevkifata Tabi İşlem Üzerinden Hes. KDV</xsl:text>
													</span>
												</td>
												<td class="lineTableBudgetTd" style="width:82px; " align="right">
													<xsl:value-of
															select="format-number(sum(n1:Invoice/cac:TaxTotal/cac:TaxSubtotal[cac:TaxCategory/cac:TaxScheme/cbc:TaxTypeCode=9015]/cbc:TaxableAmount), '###.##0,00', 'european')"/>
													<xsl:if test="n1:Invoice/cbc:DocumentCurrencyCode = 'TRL'">
														<xsl:text>TL</xsl:text>
													</xsl:if>
													<xsl:if test="n1:Invoice/cbc:DocumentCurrencyCode != 'TRL'">
														<xsl:value-of select="n1:Invoice/cbc:DocumentCurrencyCode"/>
													</xsl:if>
												</td>
											</tr>
										</xsl:if>
										<xsl:if test="n1:Invoice/cac:InvoiceLine[cac:WithholdingTaxTotal/cac:TaxSubtotal/cac:TaxCategory/cac:TaxScheme]">
											<tr align="right">
												<td/>
												<td class="lineTableBudgetTd" width="211px" align="right">
													<span style="font-weight:bold; ">
														<xsl:text>Tevkifata Tabi İşlem Tutarı</xsl:text>
													</span>
												</td>
												<td class="lineTableBudgetTd" style="width:82px; " align="right">
													<xsl:if test="n1:Invoice/cac:InvoiceLine[cac:WithholdingTaxTotal/cac:TaxSubtotal/cac:TaxCategory/cac:TaxScheme]">
														<xsl:value-of
																select="format-number(sum(n1:Invoice/cac:InvoiceLine[cac:WithholdingTaxTotal/cac:TaxSubtotal/cac:TaxCategory/cac:TaxScheme]/cbc:LineExtensionAmount), '###.##0,00', 'european')"
														/>
													</xsl:if>
													<xsl:if test="//n1:Invoice/cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cac:TaxScheme/cbc:TaxTypeCode=&apos;9015&apos;">
														<xsl:value-of
																select="format-number(sum(n1:Invoice/cac:InvoiceLine[cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cac:TaxScheme/cbc:TaxTypeCode=9015]/cbc:LineExtensionAmount), '###.##0,00', 'european')"
														/>
													</xsl:if>
													<xsl:if test="n1:Invoice/cbc:DocumentCurrencyCode = 'TRL' or n1:Invoice/cbc:DocumentCurrencyCode = 'TRY'">
														<xsl:text>TL</xsl:text>
													</xsl:if>
													<xsl:if test="n1:Invoice/cbc:DocumentCurrencyCode != 'TRL' and n1:Invoice/cbc:DocumentCurrencyCode != 'TRY'">
														<xsl:value-of select="n1:Invoice/cbc:DocumentCurrencyCode"/>
													</xsl:if>
												</td>
											</tr>
											<tr align="right">
												<td/>
												<td class="lineTableBudgetTd" width="211px" align="right">
													<span style="font-weight:bold; ">
														<xsl:text>Tevkifata Tabi İşlem Üzerinden Hes. KDV</xsl:text>
													</span>
												</td>
												<td class="lineTableBudgetTd" style="width:82px; " align="right">
													<xsl:if test="n1:Invoice/cac:InvoiceLine[cac:WithholdingTaxTotal/cac:TaxSubtotal/cac:TaxCategory/cac:TaxScheme]">
														<xsl:value-of
																select="format-number(sum(n1:Invoice/cac:WithholdingTaxTotal/cac:TaxSubtotal[cac:TaxCategory/cac:TaxScheme]/cbc:TaxableAmount), '###.##0,00', 'european')"
														/>
													</xsl:if>
													<xsl:if test="//n1:Invoice/cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cac:TaxScheme/cbc:TaxTypeCode=&apos;9015&apos;">
														<xsl:value-of
																select="format-number(sum(n1:Invoice/cac:TaxTotal/cac:TaxSubtotal[cac:TaxCategory/cac:TaxScheme/cbc:TaxTypeCode=9015]/cbc:TaxableAmount), '###.##0,00', 'european')"
														/>
													</xsl:if>
													<xsl:if test="n1:Invoice/cbc:DocumentCurrencyCode = 'TRL' or n1:Invoice/cbc:DocumentCurrencyCode = 'TRY'">
														<xsl:text>TL</xsl:text>
													</xsl:if>
													<xsl:if test="n1:Invoice/cbc:DocumentCurrencyCode != 'TRL' and n1:Invoice/cbc:DocumentCurrencyCode != 'TRY'">
														<xsl:value-of select="n1:Invoice/cbc:DocumentCurrencyCode"/>
													</xsl:if>
												</td>
											</tr>
										</xsl:if>

										<xsl:if test="not($varfaturatipi='SGK' and $varoptik='medula') and  $varExportCarriage &gt; 0">
											<tr align="right">
												<td/>
												<td class="lineTableBudgetTd" width="200px" align="right">
													<span style="font-weight:bold; ">
														<xsl:text>Navlun</xsl:text>
													</span>
												</td>
												<td class="lineTableBudgetTd" style="width:82px; " align="right">
													<xsl:value-of
															select="format-number(sum(//n1:Invoice/cac:InvoiceLine/cac:Delivery/cac:Shipment/cbc:DeclaredForCarriageValueAmount), '###.##0,00', 'european')"/>
													<xsl:if
															test="//n1:Invoice/cac:InvoiceLine/cac:Delivery/cac:Shipment/cbc:DeclaredForCarriageValueAmount/@currencyID">
														<xsl:text> </xsl:text>
														<xsl:if
																test="//n1:Invoice/cac:InvoiceLine/cac:Delivery/cac:Shipment/cbc:DeclaredForCarriageValueAmount/@currencyID = 'TRL' or //n1:Invoice/cac:InvoiceLine/cac:Delivery/cac:Shipment/cbc:DeclaredForCarriageValueAmount/@currencyID = 'TRY'">
															<xsl:text>TL</xsl:text>
														</xsl:if>
														<xsl:if
																test="//n1:Invoice/cac:InvoiceLine/cac:Delivery/cac:Shipment/cbc:DeclaredForCarriageValueAmount/@currencyID != 'TRL' and //n1:Invoice/cac:InvoiceLine/cac:Delivery/cac:Shipment/cbc:DeclaredForCarriageValueAmount/@currencyID != 'TRY'">
															<xsl:value-of
																	select="//n1:Invoice/cac:InvoiceLine/cac:Delivery/cac:Shipment/cbc:DeclaredForCarriageValueAmount/@currencyID"
															/>
														</xsl:if>
													</xsl:if>
												</td>
											</tr>
										</xsl:if>
										<xsl:if test="not($varfaturatipi='SGK' and $varoptik='medula') and  $varExportInsurance &gt; 0">
											<tr align="right">
												<td/>
												<td class="lineTableBudgetTd" width="200px" align="right">
													<span style="font-weight:bold; ">
														<xsl:text>Sigorta</xsl:text>
													</span>
												</td>
												<td class="lineTableBudgetTd" style="width:82px; " align="right">
													<xsl:value-of
															select="format-number(sum(//n1:Invoice/cac:InvoiceLine/cac:Delivery/cac:Shipment/cbc:InsuranceValueAmount), '###.##0,00', 'european')"/>
													<xsl:if
															test="//n1:Invoice/cac:InvoiceLine/cac:Delivery/cac:Shipment/cbc:InsuranceValueAmount/@currencyID">
														<xsl:text> </xsl:text>
														<xsl:if
																test="//n1:Invoice/cac:InvoiceLine/cac:Delivery/cac:Shipment/cbc:InsuranceValueAmount/@currencyID = 'TRL' or //n1:Invoice/cac:InvoiceLine/cac:Delivery/cac:Shipment/cbc:InsuranceValueAmount/@currencyID = 'TRY'">
															<xsl:text>TL</xsl:text>
														</xsl:if>
														<xsl:if
																test="//n1:Invoice/cac:InvoiceLine/cac:Delivery/cac:Shipment/cbc:InsuranceValueAmount/@currencyID != 'TRL' and //n1:Invoice/cac:InvoiceLine/cac:Delivery/cac:Shipment/cbc:InsuranceValueAmount/@currencyID != 'TRY'">
															<xsl:value-of
																	select="//n1:Invoice/cac:InvoiceLine/cac:Delivery/cac:Shipment/cbc:InsuranceValueAmount/@currencyID"
															/>
														</xsl:if>
													</xsl:if>
												</td>
											</tr>
										</xsl:if>
										<xsl:if test="not($varfaturatipi='SGK' and $varoptik='medula')">
											<tr align="right">
												<td/>
												<td class="lineTableBudgetTd" width="200px" align="right">
													<span style="font-weight:bold; ">
														<xsl:text>Vergiler Dahil Toplam Tutar</xsl:text>
													</span>
												</td>
												<td class="lineTableBudgetTd" style="width:82px; " align="right">
													<xsl:for-each
															select="n1:Invoice/cac:LegalMonetaryTotal/cbc:TaxInclusiveAmount">
														<xsl:call-template name="Curr_Type"/>
													</xsl:for-each>
												</td>
											</tr>
										</xsl:if>

										<xsl:if test="(//n1:Invoice/cbc:ProfileID='HKS' and //n1:Invoice/cbc:InvoiceTypeCode='KOMISYONCU') or (//n1:Invoice/cbc:ProfileID='EARSIVFATURA' and //n1:Invoice/cbc:InvoiceTypeCode='HKSKOMISYONCU')">
											<tr align="right">
												<td/>
												<td class="lineTableBudgetTd" width="200px" align="right">
													<span style="font-weight:bold; ">
														<xsl:text>Toplam Masraflar</xsl:text>
													</span>
												</td>
												<td class="lineTableBudgetTd" style="width:82px; " align="right">
													<xsl:for-each select="n1:Invoice/cac:LegalMonetaryTotal/cbc:ChargeTotalAmount">
														<xsl:call-template name="Curr_Type"/>
													</xsl:for-each>
												</td>
											</tr>
										</xsl:if>
										<xsl:if test="not($varfaturatipi='SGK') ">
											<tr align="right">
												<td/>
												<td class="lineTableBudgetTd" width="200px" align="right">
													<span style="font-weight:bold; ">
														<xsl:text>Ödenecek Tutar</xsl:text>
													</span>
												</td>
												<td class="lineTableBudgetTd" style="width:82px; " align="right">
													<xsl:for-each select="n1:Invoice/cac:LegalMonetaryTotal/cbc:PayableAmount">
														<xsl:call-template name="Curr_Type"/>
													</xsl:for-each>
												</td>
											</tr>
										</xsl:if>
										<xsl:for-each select="n1:Invoice/cac:Delivery/cac:Shipment/cbc:DeclaredCustomsValueAmount">
											<tr align="right">
												<td/>
												<td class="lineTableBudgetTd" width="200px" align="right">
													<span style="font-weight:bold; ">
														<xsl:text>Toplam Byn. Edl. Kıymet Değeri</xsl:text>
													</span>
												</td>
												<td class="lineTableBudgetTd" style="width:82px; " align="right">
													<xsl:call-template name="Curr_Type"/>
												</td>
											</tr>
										</xsl:for-each>
										<xsl:for-each select="n1:Invoice/cac:TaxTotal/cac:TaxSubtotal">
											<xsl:if test="//n1:Invoice/cbc:DocumentCurrencyCode != 'TRY' and //n1:Invoice/cbc:DocumentCurrencyCode != 'TRL'">
												<tr align="right">
													<td/>
													<td class="lineTableBudgetTd" align="right" width="200px">
														<span style="font-weight:bold; ">
															<xsl:text>Hesaplanan </xsl:text>
															<xsl:value-of select="cac:TaxCategory/cac:TaxScheme/cbc:Name"/>
															<xsl:text>(%</xsl:text>
															<xsl:value-of select="cbc:Percent"/>
															<xsl:text>) (TL)</xsl:text>
														</span>
													</td>
													<td class="lineTableBudgetTd" style="width:81px; " align="right">
														<span>
															<xsl:value-of
																	select="format-number(cbc:TaxAmount * //n1:Invoice/cac:PricingExchangeRate/cbc:CalculationRate, '###.##0,00', 'european')"/>
															<xsl:text> TL</xsl:text>
														</span>
													</td>
												</tr>
											</xsl:if>
										</xsl:for-each>
										<xsl:if test="($varfaturatipi='SGK' and not($varoptik='medula'))">
											<tr align="right">
												<td/>
												<td class="lineTableBudgetTd" align="right" width="200px">
													<span style="font-weight:bold; ">
														<xsl:text>Toplam Ödenecek Tutar</xsl:text>
													</span>
												</td>
												<td class="lineTableBudgetTd" style="width:82px; " align="right">
													<xsl:for-each select="n1:Invoice/cac:LegalMonetaryTotal/cbc:PayableAmount">
														<xsl:call-template name="Curr_Type"/>
													</xsl:for-each>
												</td>
											</tr>
										</xsl:if>
										<xsl:if test="($varfaturatipi='SGK' and $varoptik='medula')">
											<tr align="right">
												<td/>
												<td class="lineTableBudgetTd" align="right" width="200px">
													<span style="font-weight:bold; ">
														<xsl:text>KDV Hariç Ödenecek Tutar</xsl:text>
													</span>
												</td>
												<td class="lineTableBudgetTd" style="width:82px; " align="right">
													<span>
														<xsl:value-of select="format-number(number(n1:Invoice/cac:LegalMonetaryTotal/cbc:PayableAmount) - (number($varkdv8) + number($varkdv10) + number($varkdv18) + number($varkdv20) + number($vareczanekdv18)+ number($vareczanekdv20)), '###.##0,00', 'european')" />
														<xsl:text> TL</xsl:text>
													</span>
												</td>
											</tr>
											<tr align="right">
												<td/>
												<td class="lineTableBudgetTd" align="right" width="200px">
													<span style="font-weight:bold; ">
														<xsl:text>KDV(%8 + %10 + %18 + %20)</xsl:text>
													</span>
												</td>
												<td class="lineTableBudgetTd" style="width:82px; " align="right">
													<span>
														<xsl:value-of select="format-number((number($varkdv8) + number($varkdv10) + number($varkdv18) + number($varkdv20) + number($vareczanekdv18) + number($vareczanekdv20)), '###.##0,00', 'european')" />
														<xsl:text> TL</xsl:text>
													</span>
												</td>
											</tr>
											<tr align="right">
												<td/>
												<td class="lineTableBudgetTd" align="right" width="200px">
													<span style="font-weight:bold; ">
														<xsl:text>Toplam Ödenecek Tutar</xsl:text>
													</span>
												</td>
												<td class="lineTableBudgetTd" style="width:82px; " align="right">
													<span style="font-weight:bold; ">
														<xsl:for-each select="n1:Invoice/cac:LegalMonetaryTotal/cbc:PayableAmount">
															<xsl:call-template name="Curr_Type"/>
														</xsl:for-each>
													</span>
												</td>
											</tr>
										</xsl:if>
										<xsl:if test="//n1:Invoice/cac:LegalMonetaryTotal/cbc:LineExtensionAmount/@currencyID != 'TRL' and //n1:Invoice/cac:LegalMonetaryTotal/cbc:LineExtensionAmount/@currencyID != 'TRY'">
											<tr align="right">
												<td/>
												<td class="lineTableBudgetTd" align="right" width="200px">
													<span style="font-weight:bold; ">
														<xsl:text>Mal Hizmet Toplam Tutarı(TL)</xsl:text>
													</span>
												</td>
												<td class="lineTableBudgetTd" style="width:81px; " align="right">
													<xsl:value-of
															select="format-number(//n1:Invoice/cac:LegalMonetaryTotal/cbc:LineExtensionAmount * //n1:Invoice/cac:PricingExchangeRate/cbc:CalculationRate, '###.##0,00', 'european')"/>
													<xsl:text> TL</xsl:text>
												</td>
											</tr>
											<tr align="right">
												<td/>
												<td class="lineTableBudgetTd" width="200px" align="right">
													<span style="font-weight:bold; ">
														<xsl:text>Vergiler Dahil Toplam Tutar(TL)</xsl:text>
													</span>
												</td>
												<td class="lineTableBudgetTd" style="width:82px; " align="right">
													<xsl:value-of
															select="format-number(//n1:Invoice/cac:LegalMonetaryTotal/cbc:TaxInclusiveAmount * //n1:Invoice/cac:PricingExchangeRate/cbc:CalculationRate, '###.##0,00', 'european')"/>
													<xsl:text> TL</xsl:text>
												</td>
											</tr>
											<xsl:if test="not($varfaturatipi='SGK')">
												<tr align="right">
													<td/>
													<td class="lineTableBudgetTd" width="200px" align="right">
														<span style="font-weight:bold; ">
															<xsl:text>Vergiler Dahil Toplam Tutar</xsl:text>
														</span>
													</td>
													<td class="lineTableBudgetTd" style="width:82px; " align="right">
														<xsl:for-each select="n1:Invoice/cac:LegalMonetaryTotal/cbc:TaxInclusiveAmount">
															<xsl:call-template name="Curr_Type"/>
														</xsl:for-each>
													</td>
												</tr>
											</xsl:if>
											<tr align="right">
												<td/>
												<td class="lineTableBudgetTd" width="200px" align="right">
													<span style="font-weight:bold; ">
														<xsl:text>Ödenecek Tutar(TL)</xsl:text>
													</span>
												</td>
												<td class="lineTableBudgetTd" style="width:82px; " align="right">
													<xsl:value-of
															select="format-number(//n1:Invoice/cac:LegalMonetaryTotal/cbc:PayableAmount * //n1:Invoice/cac:PricingExchangeRate/cbc:CalculationRate, '###.##0,00', 'european')"/>
													<xsl:text> TL</xsl:text>
												</td>
											</tr>
										</xsl:if>
									</tbody>
								</table>
							</td>
						</tr>
					</tbody>
				</table>
				<br/>
				<xsl:if test="//n1:Invoice/cac:BillingReference/cac:InvoiceDocumentReference/cbc:DocumentTypeCode[text()='İADE' or text()='IADE']">
					<table id="lineTable" width="800">
						<thead>
							<tr>
								<td align="left">
									<span style="font-weight:bold; " align="center">&#160;&#160;&#160;&#160;&#160;İadeye Konu Olan Faturalar</span>
								</td>
							</tr>
						</thead>
						<tbody>
							<tr align="left" class="lineTableTr">
								<td class="lineTableTd">
									<span style="font-weight:bold; " align="center">&#160;&#160;&#160;&#160;&#160;Fatura No</span>
								</td>
								<td class="lineTableTd">
									<span style="font-weight:bold; " align="center">&#160;&#160;&#160;&#160;&#160;Tarih</span>
								</td>
							</tr>
							<xsl:for-each select="//n1:Invoice/cac:BillingReference/cac:InvoiceDocumentReference/cbc:DocumentTypeCode[text()='İADE' or text()='IADE']">
								<tr align="left" class="lineTableTr">
									<td class="lineTableTd">&#160;&#160;&#160;&#160;&#160;
										<xsl:value-of select="../cbc:ID"/>
									</td>
									<td class="lineTableTd">&#160;&#160;&#160;&#160;&#160;
										<xsl:for-each select="../cbc:IssueDate">
											<xsl:apply-templates select="."/>
										</xsl:for-each>
									</td>
								</tr>
							</xsl:for-each>
						</tbody>
					</table>
				</xsl:if>
				<br/>
				<xsl:if	test="//n1:Invoice/cac:BillingReference/cac:AdditionalDocumentReference/cbc:DocumentTypeCode='OKCBF'">
					<table border="1" id="lineTable" width="800">
						<thead>
							<tr>
								<th colspan="6">ÖKC Bilgileri</th>
							</tr>
						</thead>
						<tbody>
							<tr id="okcbfHeadTr" style="font-weight:bold;">
								<td style="width:20%">
									<xsl:text>Fiş Numarası</xsl:text>
								</td>
								<td style="width:10%" align="center">
									<xsl:text>Fiş Tarihi</xsl:text>
								</td>
								<td style="width:10%" align="center">
									<xsl:text>Fiş Saati</xsl:text>
								</td>
								<td style="width:40%" align="center">
									<xsl:text>Fiş Tipi</xsl:text>
								</td>
								<td style="width:10%" align="center">
									<xsl:text>Z Rapor No</xsl:text>
								</td>
								<td style="width:10%" align="center">
									<xsl:text>ÖKC Seri No</xsl:text>
								</td>
							</tr>
						</tbody>
						<xsl:for-each select="//n1:Invoice/cac:BillingReference/cac:AdditionalDocumentReference/cbc:DocumentTypeCode[text()='OKCBF']">
							<tr>
								<td style="width:20%">
									<xsl:value-of select="../cbc:ID"/>
								</td>
								<td style="width:10%" align="center">
									<xsl:value-of select="../cbc:IssueDate"/>
								</td>
								<td style="width:10%" align="center">
									<xsl:value-of select="substring(../cac:ValidityPeriod/cbc:StartTime,1,5)"/>
								</td>
								<td style="width:40%" align="center">
									<xsl:choose>
										<xsl:when test="../cbc:DocumentDescription='AVANS'">
											<xsl:text>Ön Tahsilat(Avans) Bilgi Fişi</xsl:text>
										</xsl:when>
										<xsl:when test="../cbc:DocumentDescription='YEMEK_FIS'">
											<xsl:text>Yemek Fişi/Kartı ile Yapılan Tahsilat Bilgi Fişi</xsl:text>
										</xsl:when>
										<xsl:when test="../cbc:DocumentDescription='E-FATURA'">
											<xsl:text>E-Fatura Bilgi Fişi</xsl:text>
										</xsl:when>
										<xsl:when test="../cbc:DocumentDescription='E-FATURA_IRSALIYE'">
											<xsl:text>İrsaliye Yerine Geçen E-Fatura Bilgi Fişi</xsl:text>
										</xsl:when>
										<xsl:when test="../cbc:DocumentDescription='E-ARSIV'">
											<xsl:text>E-Arşiv Bilgi Fişi</xsl:text>
										</xsl:when>
										<xsl:when test="../cbc:DocumentDescription='E-ARSIV_IRSALIYE'">
											<xsl:text>İrsaliye Yerine Geçen E-Arşiv Bilgi Fişi</xsl:text>
										</xsl:when>
										<xsl:when test="../cbc:DocumentDescription='FATURA'">
											<xsl:text>Faturalı Satış Bilgi Fişi</xsl:text>
										</xsl:when>
										<xsl:when test="../cbc:DocumentDescription='OTOPARK'">
											<xsl:text>Otopark Giriş Bilgi Fişi</xsl:text>
										</xsl:when>
										<xsl:when test="../cbc:DocumentDescription='FATURA_TAHSILAT'">
											<xsl:text>Fatura Tahsilat Bilgi Fişi</xsl:text>
										</xsl:when>
										<xsl:when test="../cbc:DocumentDescription='FATURA_TAHSILAT_KOMISYONLU'">
											<xsl:text>Komisyonlu Fatura Tahsilat Bilgi Fişi</xsl:text>
										</xsl:when>
										<xsl:otherwise>
											<xsl:text> </xsl:text>
										</xsl:otherwise>
									</xsl:choose>
								</td>
								<td style="width:10%" align="center">
									<xsl:value-of select="../cac:Attachment/cac:ExternalReference/cbc:URI"/>
								</td>
								<td style="width:10%" align="center">
									<xsl:value-of select="../cac:IssuerParty/cbc:EndpointID"/>
								</td>
							</tr>
						</xsl:for-each>
					</table>
					<br/>
				</xsl:if>


				<table id="notesTable" style="width: 800px;">
					<tbody>
						<xsl:if test="($varfaturatipi='SGK' and $varoptik='medula')">
							<tr>
								<td style="width: 100%;">
									<table style="margin-top: 10px; margin-left: 10px;">
										<tbody>
											<tr>
												<td style="width: 25%; vertical-align: top;">
													<table style="width: 100%;">
														<tbody>
															<!--TEBEOS Cezaevi faturası için sgk şeklinde bir tasarım istermiştir ona göre düzenleme yapılmıştır.
                                                                Resources altına oluşturdukları xml atılacaktır. Değişiklik yaparken o xmle de görede kontrol sağlanmalıdır.-->
															<xsl:if test="not($varmaasdanilackatilimpayi='null' or $varmaasdanilackatilimpayi='' or $vareldenmuayenekatilimpayi='' or $vareldenrecetekatilimpayi='' or $varfaturatype='CETAS') or $varmaasdanilackatilimpayi='null'">
																<tr>
																	<td style="width: 50%; text-decoration: underline; font-weight: bold;">
																		<xsl:text>Elden Tahsil Edilen</xsl:text>
																	</td>
																</tr>
															</xsl:if>

															<!--TEBEOS Cezaevi faturası için sgk şeklinde bir tasarım istermiştir ona göre düzenleme yapılmıştır.
                                                                Resources altına oluşturdukları xml atılacaktır. Değişiklik yaparken o xmle de görede kontrol sağlanmalıdır.-->
															<xsl:if test="not($varmaasdanilackatilimpayi='null' or $varmaasdanilackatilimpayi='' or $varfaturatype='CETAS')">
																<tr style="line-height: 14px;">
																	<td style="width: 50%;">
																		<xsl:text>İlaç Kat. Payı(Elden):</xsl:text>
																	</td>

																	<td style="width: 50%;">
																		<xsl:value-of select="format-number(number($vareldenilackatilimpayi), '###.##0,00', 'european')" />
																		<xsl:text> TL</xsl:text>
																	</td>
																</tr>
															</xsl:if>

															<!--TEBEOS Cezaevi faturası için sgk şeklinde bir tasarım istermiştir ona göre düzenleme yapılmıştır.
                                                                Resources altına oluşturdukları xml atılacaktır. Değişiklik yaparken o xmle de görede kontrol sağlanmalıdır.-->
															<xsl:if test="not($vareldenmuayenekatilimpayi='' or $varfaturatype='CETAS')">
																<tr style="line-height: 14px;">
																	<td style="width: 50%;">
																		<xsl:text>Muayene Kat. Payı(Elden):</xsl:text>
																	</td>

																	<td style="width: 50%;">
																		<xsl:value-of select="format-number(number($vareldenmuayenekatilimpayi), '###.##0,00', 'european')"/>
																		<xsl:text> TL</xsl:text>
																	</td>
																</tr>
															</xsl:if>

															<!--TEBEOS Cezaevi faturası için sgk şeklinde bir tasarım istermiştir ona göre düzenleme yapılmıştır.
                                                                Resources altına oluşturdukları xml atılacaktır. Değişiklik yaparken o xmle de görede kontrol sağlanmalıdır.-->
															<xsl:if test="not($vareldenrecetekatilimpayi='' or $varfaturatype='CETAS')">
																<tr style="line-height: 14px;">
																	<td style="width: 50%;">
																		<xsl:text>Reçete Kat. Payı(Elden):</xsl:text>
																	</td>

																	<td style="width: 50%;">
																		<xsl:value-of select="format-number(number($vareldenrecetekatilimpayi), '###.##0,00', 'european')"/>
																		<xsl:text> TL</xsl:text>
																	</td>
																</tr>
															</xsl:if>

															<xsl:if test="$varmaasdanilackatilimpayi='null'">
																<tr style="line-height: 14px;">
																	<td style="width: 60%;">
																		<xsl:text>İlaç Kat. Payı(Elden + Maaş):</xsl:text>
																	</td>

																	<td style="width: 40%;">
																		<xsl:value-of select="format-number(number($vareldenilackatilimpayi), '###.##0,00', 'european')" />
																		<xsl:text> TL</xsl:text>
																	</td>
																</tr>
															</xsl:if>


														</tbody>
													</table>
												</td>

												<td style="width: 25%; vertical-align: top;">
													<table style="width: 100%">
														<tbody>
															<!--TEBEOS Cezaevi faturası için sgk şeklinde bir tasarım istermiştir ona göre düzenleme yapılmıştır.
                                                                Resources altına oluşturdukları xml atılacaktır. Değişiklik yaparken o xmle de görede kontrol sağlanmalıdır.-->
															<xsl:if test="not($varmaasdanilackatilimpayi='null' or $varmaasdanilackatilimpayi='' or $varmaasmuayenekatilimpayi='' or $varmaastanrecetekatilimpayi='' or $varfaturatype='CETAS')">
																<tr>
																	<td style="width: 50%; text-decoration: underline; font-weight: bold;">
																		<xsl:text>Maaştan Kesilen</xsl:text>
																	</td>
																</tr>
															</xsl:if>

															<!--TEBEOS Cezaevi faturası için sgk şeklinde bir tasarım istermiştir ona göre düzenleme yapılmıştır.
                                                                Resources altına oluşturdukları xml atılacaktır. Değişiklik yaparken o xmle de görede kontrol sağlanmalıdır.-->
															<xsl:if test="not($varmaasdanilackatilimpayi='null' or $varmaasdanilackatilimpayi='' or $varfaturatype='CETAS')">
																<tr style="line-height: 14px;">
																	<td style="width: 50%;">
																		<xsl:text>İlaç Kat. Payı(Maaş)</xsl:text>
																	</td>

																	<td style="width: 50%;">
																		<xsl:value-of select="format-number(number($varmaasdanilackatilimpayi), '###.##0,00', 'european')" />
																		<xsl:text> TL</xsl:text>
																	</td>
																</tr>
															</xsl:if>

															<!--TEBEOS Cezaevi faturası için sgk şeklinde bir tasarım istermiştir ona göre düzenleme yapılmıştır.
                                                                Resources altına oluşturdukları xml atılacaktır. Değişiklik yaparken o xmle de görede kontrol sağlanmalıdır.-->
															<xsl:if test="not($varmaasmuayenekatilimpayi='' or $varfaturatype='CETAS')">
																<tr style="line-height: 14px;">
																	<td style="width: 50%;">
																		<xsl:text>Muayene Kat. Payı(Maaş)</xsl:text>
																	</td>

																	<td style="width: 50%;">
																		<xsl:value-of select="format-number(number($varmaasmuayenekatilimpayi), '###.##0,00', 'european')"/>
																		<xsl:text> TL</xsl:text>
																	</td>
																</tr>
															</xsl:if>

															<!--TEBEOS Cezaevi faturası için sgk şeklinde bir tasarım istermiştir ona göre düzenleme yapılmıştır.
                                                                Resources altına oluşturdukları xml atılacaktır. Değişiklik yaparken o xmle de görede kontrol sağlanmalıdır.-->
															<xsl:if test="not($varmaastanrecetekatilimpayi='' or $varfaturatype='CETAS')">
																<tr style="line-height: 14px;">
																	<td style="width: 50%;">
																		<xsl:text>Reçete Kat. Payı(Maaş):</xsl:text>
																	</td>

																	<td style="width: 50%;">
																		<xsl:value-of select="format-number(number($varmaastanrecetekatilimpayi), '###.##0,00', 'european')"/>
																		<xsl:text> TL</xsl:text>
																	</td>
																</tr>
															</xsl:if>
														</tbody>
													</table>
												</td>
											</tr>
										</tbody>
									</table>
								</td>
							</tr>
						</xsl:if>
						<tr align="left">
							<td id="notesTableTd" style="width: 80%" height="100">
								<xsl:for-each select="//n1:Invoice/cac:TaxTotal/cac:TaxSubtotal">
									<xsl:if test="(cac:TaxCategory/cac:TaxScheme/cbc:TaxTypeCode='0015' or ../../cbc:InvoiceTypeCode='OZELMATRAH') and cac:TaxCategory/cbc:TaxExemptionReason">
										<b>&#160;&#160;&#160;&#160;&#160; Vergi İstisna Muafiyet Sebebi: </b>
										<xsl:value-of select="cac:TaxCategory/cbc:TaxExemptionReasonCode"/>
										<xsl:text>-</xsl:text>
										<xsl:value-of select="cac:TaxCategory/cbc:TaxExemptionReason"/>
										<br/>
									</xsl:if>
									<xsl:if test="starts-with(cac:TaxCategory/cac:TaxScheme/cbc:TaxTypeCode,'007') and cac:TaxCategory/cbc:TaxExemptionReason">
										<b>&#160;&#160;&#160;&#160;&#160; ÖTV İstisna Muafiyet Sebebi: </b>
										<xsl:value-of select="cac:TaxCategory/cbc:TaxExemptionReasonCode"/>
										<xsl:text>-</xsl:text>
										<xsl:value-of select="cac:TaxCategory/cbc:TaxExemptionReason"/>
										<br/>
									</xsl:if>
								</xsl:for-each>
								<xsl:for-each select="//n1:Invoice/cac:WithholdingTaxTotal/cac:TaxSubtotal/cac:TaxCategory/cac:TaxScheme">
									<b>&#160;&#160;&#160;&#160;&#160; Tevkifat Sebebi: </b>
									<xsl:value-of select="cbc:TaxTypeCode"/>
									<xsl:text>-</xsl:text>
									<xsl:value-of select="cbc:Name"/>
									<br/>
								</xsl:for-each>

								<!-- NOTE_REF -->

								<xsl:for-each select="//n1:Invoice/cbc:Note">
									<xsl:if test="not(starts-with(.,'SGK_')) and not(starts-with(.,'FATURATIPI:SGK')) and not(starts-with(.,'SS:')) and not(starts-with(.,'FATURA_TYPE:CETAS'))">
										<b>&#160;&#160;&#160;&#160;&#160; Not: </b>
										<xsl:value-of select="."/>
										<br/>
									</xsl:if>
								</xsl:for-each>
								<xsl:for-each select="//n1:Invoice/cac:AdditionalDocumentReference">
									<xsl:if test="cbc:ID='INTERNET_SATIS'">
										<b>&#160;&#160;&#160;&#160;&#160; Not: </b>
										<xsl:text>Bu satış internet üzerinden yapılmıştır.</xsl:text>
										<br/>

										<b>&#160;&#160;&#160;&#160;&#160; Ödeme Şekli: </b>
										<xsl:value-of select="cbc:DocumentType"/>
										<br/>

										<b>&#160;&#160;&#160;&#160;&#160; Satışın Yapıldığı Web Adresi: </b>
										<xsl:value-of select="cac:IssuerParty/cbc:WebsiteURI"/>
										<br/>
										<b>&#160;&#160;&#160;&#160;&#160; Ödeme Tarihi: </b>
										<xsl:value-of select="cbc:IssueDate"/>
										<br/>
									</xsl:if>
								</xsl:for-each>
								<xsl:if test="//n1:Invoice/cac:Delivery">
									<xsl:if test="//n1:Invoice/cac:Delivery/cac:CarrierParty/cac:PartyIdentification/cbc:ID[@schemeID='VKN']">
										<b>&#160;&#160;&#160;&#160;&#160; Taşıyıcı Unvan: </b>
										<xsl:value-of select="//n1:Invoice/cac:Delivery/cac:CarrierParty/cac:PartyName/cbc:Name"/>
										<br/>
									</xsl:if>
									<xsl:if test="//n1:Invoice/cac:Delivery/cac:CarrierParty/cac:PartyIdentification/cbc:ID[@schemeID='TCKN']">
										<b>&#160;&#160;&#160;&#160;&#160; Taşıyıcı Ad-Soyad: </b>
										<xsl:value-of select="//n1:Invoice/cac:Delivery/cac:CarrierParty/cac:Person/cbc:FirstName"/>
										<xsl:text> </xsl:text>
										<xsl:value-of select="//n1:Invoice/cac:Delivery/cac:CarrierParty/cac:Person/cbc:FamilyName"/>
										<br/>
									</xsl:if>
									<b>&#160;&#160;&#160;&#160;&#160; Taşıyıcı TCKN/VKN: </b>
									<xsl:value-of select="//n1:Invoice/cac:Delivery/cac:CarrierParty/cac:PartyIdentification/cbc:ID"/>
									<br/>
									<b>&#160;&#160;&#160;&#160;&#160; Gönderim Tarihi: </b>
									<xsl:value-of select="//n1:Invoice/cac:Delivery/cbc:ActualDeliveryDate"/>
									<br/>
								</xsl:if>
								<xsl:if test="//n1:Invoice/cac:PaymentMeans/cbc:InstructionNote">
									<b>&#160;&#160;&#160;&#160;&#160; Ödeme Notu: </b>
									<xsl:value-of
											select="//n1:Invoice/cac:PaymentMeans/cbc:InstructionNote"/>
									<br/>
								</xsl:if>
								<xsl:if
										test="//n1:Invoice/cac:PaymentMeans/cac:PayeeFinancialAccount/cbc:PaymentNote">
									<b>&#160;&#160;&#160;&#160;&#160; Hesap Açıklaması: </b>
									<xsl:value-of
											select="//n1:Invoice/cac:PaymentMeans/cac:PayeeFinancialAccount/cbc:PaymentNote"/>
									<br/>
								</xsl:if>
								<xsl:if test="//n1:Invoice/cac:PaymentTerms/cbc:Note">
									<b>&#160;&#160;&#160;&#160;&#160; Ödeme Koşulu: </b>
									<xsl:value-of select="//n1:Invoice/cac:PaymentTerms/cbc:Note"/>
									<br/>
								</xsl:if>
								<xsl:if test="//n1:Invoice/cac:BuyerCustomerParty/cac:Party/cac:PartyIdentification/cbc:ID[@schemeID='PARTYTYPE']='TAXFREE' and //n1:Invoice/cac:TaxRepresentativeParty/cac:PartyTaxScheme/cbc:ExemptionReasonCode">
									<br/>
									<b>&#160;&#160;&#160;&#160;&#160; VAT OFF - NO CASH REFUND </b>
								</xsl:if>
							</td>
							<td style="width: 20%">

							</td>
						</tr>
					</tbody>
				</table>
				<!-- ORDER-REFUND -->
				<table border="1" cellpadding="1" cellspacing="1" style="width: 800px;"> 
					<tbody><tr>
					<td style="width: 239px;">
						<span style="color: rgb(68, 68, 68); font-family: verdana, geneva, sans-serif; font-size: 10px; line-height: 20.82px; text-align: center;">&#xa0; &#xa0;&#xa0;KUVEYTTÜRK KATILIM BANKASI A.Ş.</span>
					</td>
					<td style="width: 450px;">
						<span style="color: rgb(68, 68, 68); font-family: verdana, geneva, sans-serif; font-size: 10px; line-height: 20.82px; text-align: center; background-color: rgb(255, 255, 255);">&#xa0; &#xa0;&#xa0;IBAN:&#xa0;TR940020500000893443500001</span>
					</td>
				</tr>
<tr>
					<td style="width: 239px;">
						<span style="color: rgb(68, 68, 68); font-family: verdana, geneva, sans-serif; font-size: 10px; line-height: 20.82px; text-align: center;">&#xa0; &#xa0;&#xa0;DÜNYA KATILIM BANKASI A.Ş.</span>
					</td>
					<td style="width: 450px;">
						<span style="color: rgb(68, 68, 68); font-family: verdana, geneva, sans-serif; font-size: 10px; line-height: 20.82px; text-align: center; background-color: rgb(255, 255, 255);">&#xa0; &#xa0;&#xa0;IBAN:&#xa0;TR930021401000000000014954</span>
					</td>
				</tr></tbody> 
				</table>

				<div id="qrvalue" style="visibility: hidden; height: 20px;width: 20px; ; display:none">
{"vkntckn":"<xsl:value-of select="n1:Invoice/cac:AccountingSupplierParty/cac:Party/cac:PartyIdentification/cbc:ID[@schemeID='TCKN' or @schemeID='VKN']"/>",
"avkntckn":"<xsl:value-of select="n1:Invoice/cac:AccountingCustomerParty/cac:Party/cac:PartyIdentification/cbc:ID[@schemeID='TCKN' or @schemeID='VKN']"/>",
<xsl:if test="//n1:Invoice/cbc:ProfileID = 'YOLCUBERABERFATURA'">"pasaportno":"<xsl:value-of select="n1:Invoice/cac:BuyerCustomerParty/cac:Party/cac:Person/cac:IdentityDocumentReference/cbc:ID"/>",</xsl:if>
<xsl:if test="//n1:Invoice/cbc:ProfileID = 'YOLCUBERABERFATURA'">"aracikurumvkn":"<xsl:value-of select="n1:Invoice/cac:TaxRepresentativeParty/cac:PartyIdentification/cbc:ID[@schemeID='ARACIKURUMVKN']"/>",</xsl:if>
"senaryo":"<xsl:value-of select="n1:Invoice/cbc:ProfileID"/>",
"tip":"<xsl:value-of select="n1:Invoice/cbc:InvoiceTypeCode"/>",
"tarih":"<xsl:value-of select="n1:Invoice/cbc:IssueDate"/>",
"no":"<xsl:value-of select="n1:Invoice/cbc:ID"/>",
"ettn":"<xsl:value-of select="n1:Invoice/cbc:UUID"/>",
"parabirimi":"<xsl:value-of select="n1:Invoice/cbc:DocumentCurrencyCode"/>",
"malhizmettoplam":"<xsl:value-of select="n1:Invoice/cac:LegalMonetaryTotal/cbc:LineExtensionAmount"/>",<xsl:for-each select="n1:Invoice/cac:TaxTotal/cac:TaxSubtotal[cac:TaxCategory/cac:TaxScheme/cbc:TaxTypeCode='0015']">
"kdvmatrah(<xsl:value-of select="cbc:Percent"/>)":"<xsl:value-of select="cbc:TaxableAmount"/>",</xsl:for-each><xsl:for-each select="n1:Invoice/cac:TaxTotal/cac:TaxSubtotal[cac:TaxCategory/cac:TaxScheme/cbc:TaxTypeCode='0015']">
"hesaplanankdv(<xsl:value-of select="cbc:Percent"/>)":"<xsl:value-of select="cbc:TaxAmount"/>",</xsl:for-each>
"vergidahil":"<xsl:value-of select="n1:Invoice/cac:LegalMonetaryTotal/cbc:TaxInclusiveAmount"/>",
"odenecek":"<xsl:value-of select="n1:Invoice/cac:LegalMonetaryTotal/cbc:PayableAmount"/>"}
				</div>
				<script type="text/javascript">
					var qrcode = new QRCode(document.getElementById("qrcode"), {
					width : 170,
					height : 170,
					correctLevel : QRCode.CorrectLevel.L
					});

					function makeCode (msg) {
					qrcode.makeCode(msg);
					}

					makeCode(document.getElementById("qrvalue").innerHTML.replace(/\s/g, ''));
				</script>
			</body>
		</html>
	</xsl:template>
	<xsl:template match="//n1:Invoice/cac:InvoiceLine">
		<tr class="lineTableTr">
			<td class="lineTableTd">
				<xsl:text>&#160;</xsl:text>
				<xsl:value-of select="./cbc:ID"/>
			</td>
			<xsl:choose>
				<xsl:when test="$varItemCode &gt; 0">
					<td class="lineTableTd">
						<xsl:text>&#160;</xsl:text>
						<xsl:value-of select="./cac:Item/cac:SellersItemIdentification/cbc:ID"/>
					</td>
				</xsl:when>
				<xsl:otherwise>
				</xsl:otherwise>
			</xsl:choose>
			<xsl:choose>
				<xsl:when test="//n1:Invoice/cac:AccountingCustomerParty/cac:Party/cac:PartyIdentification/cbc:ID[@schemeID='VKN' and text()='7350019759']">
					<td class="lineTableTd">
						<xsl:text>&#160;</xsl:text>
						<xsl:for-each select="./cbc:Note">
							<xsl:if test="contains(.,'#SS_Satir_NO=')">
								<xsl:value-of select="normalize-space(substring-after(substring(.,12),'='))"/>
							</xsl:if>
						</xsl:for-each>
					</td>
				</xsl:when>
			</xsl:choose>
			<td class="lineTableTd">
				<xsl:text>&#160;</xsl:text>
				<xsl:value-of select="./cac:Item/cbc:Name"/>
			</td>

			<xsl:if test="not($varfaturatipi='SGK')">
				<td class="lineTableTd" align="right">
					<xsl:text>&#160;</xsl:text>
					<xsl:value-of select="format-number(./cbc:InvoicedQuantity, '###.##0,####', 'european')"/>
					<xsl:if test="./cbc:InvoicedQuantity/@unitCode">
						<xsl:for-each select="./cbc:InvoicedQuantity">
							<xsl:text> </xsl:text>
							<xsl:choose>
								<xsl:when test="@unitCode = 'BX'">
									<xsl:text>Kutu</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'TNE'">
									<xsl:text>ton</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'BX'">
									<xsl:text>Kutu</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'LTR'">
									<xsl:text>lt</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'C62'">
									<xsl:text>Adet</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'TN'">
									<xsl:text>Teneke</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'KGM'">
									<xsl:text>kg</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'KJO'">
									<xsl:text>kJ</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'GRM'">
									<xsl:text>g</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'MGM'">
									<xsl:text>mg</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'NT'">
									<xsl:text>Net Ton</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'GT'">
									<xsl:text>Gross Ton</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'MTR'">
									<xsl:text>m</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'MMT'">
									<xsl:text>mm</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'KTM'">
									<xsl:text>km</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'MLT'">
									<xsl:text>ml</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'MMQ'">
									<xsl:text>mm3</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'CLT'">
									<xsl:text>cl</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'CMK'">
									<xsl:text>cm2</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'CMQ'">
									<xsl:text>cm3</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'CMT'">
									<xsl:text>cm</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'MTK'">
									<xsl:text>m2</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'MTQ'">
									<xsl:text>m3</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'DAY'">
									<xsl:text>Gün</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'MON'">
									<xsl:text>Ay</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'PA'">
									<xsl:text>Paket</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'KWH'">
									<xsl:text>KWH</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'ANN'">
									<xsl:text>Yıl</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'HUR'">
									<xsl:text>Saat</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'D61'">
									<xsl:text>Dakika</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'D62'">
									<xsl:text>Saniye</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'CCT'">
									<xsl:text>Ton baş.taşıma kap.</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'D30'">
									<xsl:text>Brüt kalori</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'D40'">
									<xsl:text>1000 lt</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'LPA'">
									<xsl:text>saf alkol lt</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'B32'">
									<xsl:text>kg.m2</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'NCL'">
									<xsl:text>hücre adet</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'PR'">
									<xsl:text>Çift</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'R9'">
									<xsl:text>1000 m3</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'SET'">
									<xsl:text>Set</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'T3'">
									<xsl:text>1000 adet</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'PK'">
									<xsl:text>Koli</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'CR'">
									<xsl:text>Kasa/Sandık</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'BG'">
									<xsl:text>Poşet/Torba</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'GFI'">
									<xsl:text>Fıssıle İzotop Gramı</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'CEN'">
									<xsl:text>Yüz Adet</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'KPO'">
									<xsl:text>Kilogram Potasyum Oksit</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'MND'">
									<xsl:text>Kurutulmuş Net Ağırlıklı Kilogramı</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = '3I'">
									<xsl:text>Kilogram-Adet</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'KFO'">
									<xsl:text>Difosfor Pentaoksit Kilogramı</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'KHY'">
									<xsl:text>Hidrojen Peroksik Kilogramı</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'KMA'">
									<xsl:text>Metil Aminlerin Kilogramı</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'KNI'">
									<xsl:text>Azotun Kilogramı</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'KPH'">
									<xsl:text>Kilogram Potasyum Hidroksit</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'KSD'">
									<xsl:text>%90 Kuru Ürün Kilogramı</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'KSH'">
									<xsl:text>Sodyum Hidroksit Kilogramı</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'KUR'">
									<xsl:text>Uranyum Kilogramı</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'D32'">
									<xsl:text>Terawatt Saat</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'GWH'">
									<xsl:text>Gigawatt Saat</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'MWH'">
									<xsl:text>Megawatt Saat (1000 kW.h)</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'KWT'">
									<xsl:text>Kilowatt</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'DMK'">
									<xsl:text>Desimetre Kare</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'CTM'">
									<xsl:text>Karat</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'SM3'">
									<xsl:text>Standart Metreküp</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'CT'">
									<xsl:text>Karton</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'DMT'">
									<xsl:text>Desimetre</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'DMQ'">
									<xsl:text>Desimetre Küp</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'KTN'">
									<xsl:text>Kiloton</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'D93'">
									<xsl:text>Doz</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'LM'">
									<xsl:text>Metre Tül</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'BO'">
									<xsl:text>Şişe</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'H80'">
									<xsl:text>Rack Unit</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'RA'">
									<xsl:text>Rack</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'TU'">
									<xsl:text>Tüp</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'BLL'">
									<xsl:text>Fıçı</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'TC'">
									<xsl:text>Kamyon</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'PG'">
									<xsl:text>Plaka</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'DPC'">
									<xsl:text>Düzüne</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'LR'">
									<xsl:text>Tabaka</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'JOU'">
									<xsl:text>Vardiya</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'DRL'">
									<xsl:text>Rulo</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'ACR'">
									<xsl:text>Dönüm</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'E53'">
									<xsl:text>Test</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'H82'">
									<xsl:text>Puan</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'SQR'">
									<xsl:text>Ayak</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'AYR'">
									<xsl:text>Altın Ayarı</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'BAS'">
									<xsl:text>Bas</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'CPR'">
									<xsl:text>Adet-Çift</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'GMS'">
									<xsl:text>Gümüş</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'H62'">
									<xsl:text>Yüz Adet</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'KHO'">
									<xsl:text>Hidroje Peroksit Kilogramı</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'KH6'">
									<xsl:text>Kilogram-Baş</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'KOH'">
									<xsl:text>Kilogram Potasyum Hidroksit</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'KPR'">
									<xsl:text>Kilogram-Çift</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'K20'">
									<xsl:text>Kilogram Potasyum Oksit</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'K58'">
									<xsl:text>Kurutulmuş Net Ağırlıklı Kilogramı</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'K62'">
									<xsl:text>Kilogram-Adet</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'NCR'">
									<xsl:text>Karat</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'OMV'">
									<xsl:text>OTV Maktu Vergi</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'OTB'">
									<xsl:text>OTV Birim Fiyatı</xsl:text>
								</xsl:when>
								<xsl:when test="@unitCode = 'D63'">
									<xsl:text>Cilt</xsl:text>
								</xsl:when>
							</xsl:choose>
						</xsl:for-each>
					</xsl:if>
				</td>
				<xsl:if test="$varEtiketFiyati='1'">
					<td class="lineTableTd" align="right">
						<xsl:for-each select="//n1:Invoice/cac:InvoiceLine/cbc:Note">
							<xsl:if test="contains(.,'ETF:') or contains(.,'ESF:')">
								<xsl:value-of select="substring-after(substring(.,4),':')" />
								<xsl:text> </xsl:text>
								<xsl:if test="//n1:Invoice/cac:InvoiceLine/cac:Price/cbc:PriceAmount/@currencyID = &quot;TRL&quot; or //n1:Invoice/cac:InvoiceLine/cac:Price/cbc:PriceAmount/@currencyID = &quot;TRY&quot;">
									<xsl:text>TL</xsl:text>
								</xsl:if>
								<xsl:if test="//n1:Invoice/cac:InvoiceLine/cac:Price/cbc:PriceAmount/@currencyID != &quot;TRL&quot; and //n1:Invoice/cac:InvoiceLine/cac:Price/cbc:PriceAmount/@currencyID != &quot;TRY&quot;">
									<xsl:value-of select="//n1:Invoice/cac:InvoiceLine/cac:Price/cbc:PriceAmount/@currencyID"/>
								</xsl:if>
							</xsl:if>
						</xsl:for-each>
					</td>
				</xsl:if>
				<td class="lineTableTd" align="right">
					<xsl:text>&#160;</xsl:text>
					<xsl:value-of
							select="format-number(./cac:Price/cbc:PriceAmount, '###.##0,########', 'european')"/>
					<xsl:if test="./cac:Price/cbc:PriceAmount/@currencyID">
						<xsl:text> </xsl:text>
						<xsl:if test="./cac:Price/cbc:PriceAmount/@currencyID = &quot;TRL&quot; or ./cac:Price/cbc:PriceAmount/@currencyID = &quot;TRY&quot;">
							<xsl:text>TL</xsl:text>
						</xsl:if>
						<xsl:if test="./cac:Price/cbc:PriceAmount/@currencyID != &quot;TRL&quot; and ./cac:Price/cbc:PriceAmount/@currencyID != &quot;TRY&quot;">
							<xsl:value-of select="./cac:Price/cbc:PriceAmount/@currencyID"/>
						</xsl:if>
					</xsl:if>
				</td>
				<xsl:if test="$varDepocuFiyati='1'">
					<td class="lineTableTd" align="right">
						<xsl:text>&#160;</xsl:text>
						<xsl:for-each select="//n1:Invoice/cac:InvoiceLine/cbc:Note">
							<xsl:if test="contains(.,'DSF:')">
								<br/>
								<xsl:value-of select="substring-after(substring(.,4),':')" />
								<xsl:text> </xsl:text>
								<xsl:if test="//n1:Invoice/cac:InvoiceLine/cac:Price/cbc:PriceAmount/@currencyID = &quot;TRL&quot; or //n1:Invoice/cac:InvoiceLine/cac:Price/cbc:PriceAmount/@currencyID = &quot;TRY&quot;">
									<xsl:text>TL</xsl:text>
								</xsl:if>
								<xsl:if test="//n1:Invoice/cac:InvoiceLine/cac:Price/cbc:PriceAmount/@currencyID != &quot;TRL&quot; and .//n1:Invoice/cac:InvoiceLine/cac:Price/cbc:PriceAmount/@currencyID != &quot;TRY&quot;">
									<xsl:value-of select="//n1:Invoice/cac:InvoiceLine/cac:Price/cbc:PriceAmount/@currencyID"/>
								</xsl:if>
							</xsl:if>
						</xsl:for-each>
						<br/>
					</td>
				</xsl:if>
				<xsl:if test="$varEczaciKar='1'">
					<td class="lineTableTd" align="right">
						<xsl:text>&#160;</xsl:text>
						<xsl:for-each select="//n1:Invoice/cac:InvoiceLine/cbc:Note">
							<xsl:if test="contains(.,'ECK:') or contains(.,'EKO:')">
								<xsl:text>%</xsl:text>
								<xsl:value-of select="substring-after(substring(.,4),':')" />
								<xsl:text> </xsl:text>
							</xsl:if>
						</xsl:for-each>
					</td>
				</xsl:if>
				<xsl:if test="$varKurumIskonto='1'">
					<td class="lineTableTd" align="right">
						<xsl:for-each select="//n1:Invoice/cac:InvoiceLine/cbc:Note">
							<xsl:if test="contains(.,'KRI:')">
								<xsl:value-of select="substring-after(substring(.,4),':')" />
								<xsl:text> </xsl:text>
								<xsl:if test="//n1:Invoice/cac:InvoiceLine/cac:Price/cbc:PriceAmount/@currencyID = &quot;TRL&quot; or //n1:Invoice/cac:InvoiceLine/cac:Price/cbc:PriceAmount/@currencyID = &quot;TRY&quot;">
									<xsl:text>TL</xsl:text>
								</xsl:if>
								<xsl:if test="//n1:Invoice/cac:InvoiceLine/cac:Price/cbc:PriceAmount/@currencyID != &quot;TRL&quot; and //n1:Invoice/cac:InvoiceLine/cac:Price/cbc:PriceAmount/@currencyID != &quot;TRY&quot;">
									<xsl:value-of select="//n1:Invoice/cac:InvoiceLine/cac:Price/cbc:PriceAmount/@currencyID"/>
								</xsl:if>
							</xsl:if>
						</xsl:for-each>
					</td>
				</xsl:if>
				<xsl:if test="$varVade='1'">
					<td class="lineTableTd" align="right">
						<xsl:text>&#160;</xsl:text>
						<xsl:for-each select="//n1:Invoice/cac:InvoiceLine/cbc:Note">
							<xsl:if test="contains(.,'VAD:')">
								<xsl:value-of select="substring-after(substring(.,4),':')" />
								<xsl:text> </xsl:text>
							</xsl:if>
						</xsl:for-each>
						<br/>
					</td>
				</xsl:if>
				<xsl:if test="$varAllowanceRate &gt; 0">
					<td class="lineTableTd" align="right">
						<xsl:text>&#160;</xsl:text>
						<xsl:for-each select="./cac:AllowanceCharge/cbc:MultiplierFactorNumeric">
							<xsl:choose>
								<xsl:when test="../cbc:ChargeIndicator='true'">
									<xsl:text>(+) %</xsl:text>
								</xsl:when>
								<xsl:otherwise>
									<xsl:text>(-) %</xsl:text>
								</xsl:otherwise>
							</xsl:choose>
							<xsl:value-of select="format-number(. * 100, '###.##0,00', 'european')"/>
							<br/>
						</xsl:for-each>
					</td>
				</xsl:if>
				<xsl:if test="$varAllowanceAmount &gt; 0">
					<td class="lineTableTd" align="right">
						<xsl:text>&#160;</xsl:text>
						<xsl:for-each select="cac:AllowanceCharge/cbc:Amount">
							<xsl:call-template name="Curr_Type"/>
							<br/>
						</xsl:for-each>
					</td>
				</xsl:if>
				<xsl:if test="$varAllowanceReason &gt; 0">
					<td class="lineTableTd" align="right">
						<xsl:text>&#160;</xsl:text>
						<xsl:for-each select="cac:AllowanceCharge/cbc:AllowanceChargeReason">

							<xsl:choose>
								<xsl:when test="../cbc:ChargeIndicator='true'">
									<xsl:text>Arttırım - </xsl:text>
								</xsl:when>
								<xsl:otherwise>
									<xsl:text>İskonto - </xsl:text>
								</xsl:otherwise>
							</xsl:choose>
							<xsl:apply-templates/>
							<br/>
						</xsl:for-each>
					</td>
				</xsl:if>
				<td class="lineTableTd" align="right">
					<xsl:text>&#160;</xsl:text>
					<xsl:for-each
							select="./cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cac:TaxScheme">
						<xsl:if test="cbc:TaxTypeCode='0015' ">
							<xsl:text> </xsl:text>
							<xsl:if test="../../cbc:Percent">
								<xsl:text> %</xsl:text>
								<xsl:value-of select="format-number(../../cbc:Percent, '###.##0,00', 'european')"
								/>
							</xsl:if>
						</xsl:if>
					</xsl:for-each>
				</td>
				<td class="lineTableTd" align="right">
					<xsl:text>&#160;</xsl:text>
					<xsl:for-each
							select="./cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cac:TaxScheme">
						<xsl:if test="cbc:TaxTypeCode='0015' ">
							<xsl:text> </xsl:text>
							<xsl:for-each select="../../cbc:TaxAmount">
								<xsl:call-template name="Curr_Type"/>
							</xsl:for-each>
						</xsl:if>
					</xsl:for-each>
				</td>
				<xsl:if test="//n1:Invoice/cac:InvoiceLine/cac:OrderLineReference/cac:OrderReference">
					<td class="lineTableTd" style="font-size: xx-small" align="right">
						<xsl:value-of select="./cac:OrderLineReference/cac:OrderReference/cbc:ID"/>
					</td>
				</xsl:if>
				<xsl:if test="//n1:Invoice/cac:InvoiceLine/cac:DespatchLineReference/cac:DocumentReference">
					<td class="lineTableTd" style="font-size: xx-small" align="right">
						<xsl:value-of select="./cac:DespatchLineReference/cac:DocumentReference/cbc:ID"/>
					</td>
				</xsl:if>
				<td class="lineTableTd" style="font-size: xx-small" align="right">
					<xsl:text>&#160;</xsl:text>
					<xsl:for-each
							select="./cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cac:TaxScheme">
						<xsl:if test="cbc:TaxTypeCode!='0015' ">
							<xsl:text> </xsl:text>
							<xsl:value-of select="cbc:Name"/>
							<xsl:if test="../../cbc:Percent">
								<xsl:text> (%</xsl:text>
								<xsl:value-of
										select="format-number(../../cbc:Percent, '###.##0,00', 'european')"/>
								<xsl:text>)=</xsl:text>
							</xsl:if>
							<xsl:for-each select="../../cbc:TaxAmount">
								<xsl:call-template name="Curr_Type"/>
							</xsl:for-each>
						</xsl:if>
					</xsl:for-each>

					<xsl:for-each select="./cac:WithholdingTaxTotal/cac:TaxSubtotal/cac:TaxCategory/cac:TaxScheme">
						<xsl:text>KDV TEVKİFAT </xsl:text>
						<xsl:if test="../../cbc:Percent">
							<xsl:text> (%</xsl:text>
							<xsl:value-of
									select="format-number(../../cbc:Percent, '###.##0,00', 'european')"/>
							<xsl:text>)=</xsl:text>
						</xsl:if>
						<xsl:for-each select="../../cbc:TaxAmount">
							<xsl:call-template name="Curr_Type"/>
							<xsl:text>&#10;</xsl:text>
						</xsl:for-each>
					</xsl:for-each>
					<xsl:for-each select="./cbc:Note">
						<xsl:if test="contains(.,'AVANS MAHSUBU')">
							<br/>
							<xsl:value-of select="." />
						</xsl:if>
						<xsl:if test="contains(.,'NAKİT TEMİNAT KESİNTİSİ')">
							<br/>
							<xsl:value-of select="." />
						</xsl:if>
					</xsl:for-each>
				</td>
				<xsl:if test="$varLineExplanation &gt; 0">
					<td class="lineTableTd" align="right">
						<xsl:text>&#160;</xsl:text>
						<xsl:for-each select="cbc:Note">
							<xsl:if test="not(contains(.,'#SS_Satir_NO=')) and not(contains(.,'AVANS MAHSUBU')) and not(contains(.,'NAKİT TEMİNAT KESİNTİSİ'))
						and not(contains(.,'ECK:')) and not(contains(.,'ETF:')) and not(contains(.,'KRI:')) and not(contains(.,'VAD:')) and not(contains(.,'DSF:'))">
								<xsl:text>&#160;</xsl:text>
								<xsl:apply-templates/>
							</xsl:if>

						</xsl:for-each>
					</td>
				</xsl:if>
			</xsl:if>
			<td class="lineTableTd" align="right">
				<xsl:text>&#160;</xsl:text>
				<xsl:for-each select="cbc:LineExtensionAmount">
					<xsl:call-template name="Curr_Type"/>
				</xsl:for-each>
			</td>
			<xsl:if test="//n1:Invoice/cbc:InvoiceTypeCode='TEVKIFATIADE'">
				<td class="lineTableTd" align="right">
					<xsl:text>&#160;</xsl:text>
					<xsl:for-each select="./cac:TaxTotal/cac:TaxSubtotal/cbc:TaxableAmount">
						<xsl:call-template name="Curr_Type"/>
					</xsl:for-each>
				</td>
			</xsl:if>
			<xsl:if test="//n1:Invoice/cbc:ProfileID='EARSIVFATURA' and //n1:Invoice/cbc:InvoiceTypeCode='ISTISNA'">
				<td class="lineTableTd" align="right">
					<xsl:text>&#160;</xsl:text>
					<xsl:value-of select="cac:Delivery/cac:Shipment/cac:GoodsItem/cbc:RequiredCustomsID"/>
				</td>
			</xsl:if>
			<xsl:if test="//n1:Invoice/cbc:ProfileID='HKS' or /n1:Invoice/cbc:InvoiceTypeCode='HKSSATIS' or /n1:Invoice/cbc:InvoiceTypeCode='HKSKOMISYONCU'">
				<td class="lineTableTd" align="right">
					<xsl:text>&#160;</xsl:text>
					<xsl:for-each
							select="cac:Item/cac:AdditionalItemIdentification/cbc:ID[@schemeID='KUNYENO']">
						<xsl:text>&#160;</xsl:text>
						<xsl:apply-templates/>
					</xsl:for-each>
				</td>
			</xsl:if>
			<xsl:if test="//n1:Invoice/cbc:ProfileID='HKS' and /n1:Invoice/cbc:InvoiceTypeCode='SATIS'">
				<td class="lineTableTd" align="right">
					<xsl:text>&#160;</xsl:text>
					<xsl:for-each
							select="cac:Item/cac:AdditionalItemIdentification/cbc:ID[@schemeID='MALSAHIBIVKNTCKN']">
						<xsl:text>&#160;</xsl:text>
						<xsl:apply-templates/>
					</xsl:for-each>
				</td>
				<td class="lineTableTd" align="right">
					<xsl:text>&#160;</xsl:text>
					<xsl:for-each
							select="cac:Item/cac:AdditionalItemIdentification/cbc:ID[@schemeID='MALSAHIBIADSOYADUNVAN']">
						<xsl:text>&#160;</xsl:text>
						<xsl:apply-templates/>
					</xsl:for-each>
				</td>
			</xsl:if>
			<xsl:if test="//n1:Invoice/cbc:InvoiceTypeCode='HKSSATIS'">
				<td class="lineTableTd" align="right">
					<xsl:text>&#160;</xsl:text>
					<xsl:for-each
							select="cac:Item/cac:AdditionalItemIdentification/cbc:ID[@schemeID='MALSAHIBIVKNTCKN']">
						<xsl:text>&#160;</xsl:text>
						<xsl:apply-templates/>
					</xsl:for-each>
				</td>
				<td class="lineTableTd" align="right">
					<xsl:text>&#160;</xsl:text>
					<xsl:for-each
							select="cac:Item/cac:AdditionalItemIdentification/cbc:ID[@schemeID='MALSAHIBIADSOYADUNVAN']">
						<xsl:text>&#160;</xsl:text>
						<xsl:apply-templates/>
					</xsl:for-each>
				</td>
			</xsl:if>
			<xsl:if test="//n1:Invoice/cbc:ProfileID='IHRACAT' or //n1:Invoice/cbc:ProfileID='OZELFATURA'">
				<td class="lineTableTd" align="right">
					<xsl:text>&#160;</xsl:text>
					<xsl:for-each select="cac:Delivery/cac:DeliveryTerms/cbc:ID[@schemeID='INCOTERMS']">
						<xsl:text>&#160;</xsl:text>
						<xsl:apply-templates/>
					</xsl:for-each>
				</td>
				<td class="lineTableTd" align="right">
					<xsl:text>&#160;</xsl:text>
					<xsl:for-each select="cac:Delivery/cac:Shipment/cac:TransportHandlingUnit/cac:ActualPackage/cbc:PackagingTypeCode">
						<xsl:text>&#160;</xsl:text>
						<xsl:call-template name="Packaging">
							<xsl:with-param name="PackagingType">
								<xsl:value-of select="."/>
							</xsl:with-param>
						</xsl:call-template>
					</xsl:for-each>
				</td>
				<td class="lineTableTd" align="right">
					<xsl:text>&#160;</xsl:text>
					<xsl:for-each select="cac:Delivery/cac:Shipment/cac:TransportHandlingUnit/cac:ActualPackage/cbc:ID">
						<xsl:text>&#160;</xsl:text>
						<xsl:apply-templates/>
					</xsl:for-each>
				</td>
				<td class="lineTableTd" align="right">
					<xsl:text>&#160;</xsl:text>
					<xsl:value-of
							select="format-number(cac:Delivery/cac:Shipment/cac:TransportHandlingUnit/cac:ActualPackage/cbc:Quantity, '###.##0,00', 'european')"/>
				</td>
				<td class="lineTableTd" align="right">
					<xsl:text>&#160;</xsl:text>
					<xsl:for-each select="cac:Delivery/cac:DeliveryAddress">
						<xsl:text>&#160;</xsl:text>
						<xsl:apply-templates/>
					</xsl:for-each>
				</td>
				<td class="lineTableTd" align="right">
					<xsl:text>&#160;</xsl:text>
					<xsl:for-each select="cac:Delivery/cac:Shipment/cac:ShipmentStage/cbc:TransportModeCode">
						<xsl:text>&#160;</xsl:text>
						<xsl:call-template name="TransportMode">
							<xsl:with-param name="TransportModeType">
								<xsl:value-of select="."/>
							</xsl:with-param>
						</xsl:call-template>
					</xsl:for-each>
				</td>
				<td class="lineTableTd" align="right">
					<xsl:text>&#160;</xsl:text>
					<xsl:for-each select="cac:Delivery/cac:Shipment/cac:GoodsItem/cbc:RequiredCustomsID">
						<xsl:text>&#160;</xsl:text>
						<xsl:apply-templates/>
					</xsl:for-each>
				</td>
				<td class="lineTableTd" align="right">
					<xsl:text>&#160;</xsl:text>
					<xsl:for-each select="cac:Delivery/cac:Shipment/cbc:DeclaredCustomsValueAmount">
						<xsl:call-template name="Curr_Type"/>
					</xsl:for-each>
				</td>
			</xsl:if>
		</tr>
	</xsl:template>
	<xsl:template match="//cbc:IssueDate">
		<xsl:value-of select="substring(.,9,2)"/>-<xsl:value-of select="substring(.,6,2)"/>-<xsl:value-of select="substring(.,1,4)"/>
	</xsl:template>
	<xsl:template match="//cbc:StartDate">
		<xsl:value-of select="substring(.,9,2)"/>-<xsl:value-of select="substring(.,6,2)"/>-<xsl:value-of select="substring(.,1,4)"/>
	</xsl:template>
	<xsl:template match="//cbc:EndDate">
		<xsl:value-of select="substring(.,9,2)"/>-<xsl:value-of select="substring(.,6,2)"/>-<xsl:value-of select="substring(.,1,4)"/>
	</xsl:template>
	<xsl:template match="//n1:Invoice">
		<tr class="lineTableTr">
			<td class="lineTableTd">
				<xsl:text>&#160;</xsl:text>
			</td>
			<td class="lineTableTd">
				<xsl:text>&#160;</xsl:text>
			</td>
			<td class="lineTableTd" align="right">
				<xsl:text>&#160;</xsl:text>
			</td>
			<td class="lineTableTd" align="right">
				<xsl:text>&#160;</xsl:text>
			</td>
			<td class="lineTableTd" align="right">
				<xsl:text>&#160;</xsl:text>
			</td>
			<td class="lineTableTd" align="right">
				<xsl:text>&#160;</xsl:text>
			</td>
			<td class="lineTableTd" align="right">
				<xsl:text>&#160;</xsl:text>
			</td>
			<td class="lineTableTd" align="right">
				<xsl:text>&#160;</xsl:text>
			</td>
			<td class="lineTableTd" align="right">
				<xsl:text>&#160;</xsl:text>
			</td>
			<td class="lineTableTd" align="right">
				<xsl:text>&#160;</xsl:text>
			</td>
			<td class="lineTableTd" align="right">
				<xsl:text>&#160;</xsl:text>
			</td>
			<xsl:if test="//n1:Invoice/cbc:ProfileID='HKS'">
				<td class="lineTableTd" align="right">
					<xsl:text>&#160;</xsl:text>
				</td>
			</xsl:if>
			<xsl:if test="//n1:Invoice/cbc:ProfileID='HKS' and /n1:Invoice/cbc:InvoiceTypeCode='SATIS'">
				<td class="lineTableTd" align="right">
					<xsl:text>&#160;</xsl:text>
				</td>
				<td class="lineTableTd" align="right">
					<xsl:text>&#160;</xsl:text>
				</td>
			</xsl:if>
			<xsl:if test="//n1:Invoice/cbc:ProfileID='IHRACAT' or //n1:Invoice/cbc:ProfileID='OZELFATURA'">
				<td class="lineTableTd" align="right">
					<xsl:text>&#160;</xsl:text>
				</td>
				<td class="lineTableTd" align="right">
					<xsl:text>&#160;</xsl:text>
				</td>
				<td class="lineTableTd" align="right">
					<xsl:text>&#160;</xsl:text>
				</td>
				<td class="lineTableTd" align="right">
					<xsl:text>&#160;</xsl:text>
				</td>
				<td class="lineTableTd" align="right">
					<xsl:text>&#160;</xsl:text>
				</td>
				<td class="lineTableTd" align="right">
					<xsl:text>&#160;</xsl:text>
				</td>
				<td class="lineTableTd" align="right">
					<xsl:text>&#160;</xsl:text>
				</td>
				<td class="lineTableTd" align="right">
					<xsl:text>&#160;</xsl:text>
				</td>
			</xsl:if>
		</tr>
	</xsl:template>
	<xsl:template name="Party_Title" >
		<xsl:param name="PartyType" />
		<td style="width:469px; " align="left">
			<xsl:if test="cac:PartyName">
				<xsl:value-of select="cac:PartyName/cbc:Name"/>
				<br/>
			</xsl:if>
			<xsl:if test="cac:PartyLegalEntity">
				<xsl:text>Vergi No:</xsl:text>
				<xsl:value-of select="cac:PartyLegalEntity/cbc:CompanyID"/>
				<br/>
			</xsl:if>
			<xsl:for-each select="cac:Person">
				<xsl:for-each select="cbc:Title">
					<xsl:apply-templates/>
					<xsl:text>&#160;</xsl:text>
				</xsl:for-each>
				<xsl:for-each select="cbc:FirstName">
					<xsl:apply-templates/>
					<xsl:text>&#160;</xsl:text>
				</xsl:for-each>
				<xsl:for-each select="cbc:MiddleName">
					<xsl:apply-templates/>
					<xsl:text>&#160; </xsl:text>
				</xsl:for-each>
				<xsl:for-each select="cbc:FamilyName">
					<xsl:apply-templates/>
					<xsl:text>&#160;</xsl:text>
				</xsl:for-each>
				<xsl:for-each select="cbc:NameSuffix">
					<xsl:apply-templates/>
				</xsl:for-each>
				<xsl:if test="$PartyType='TAXFREE'">
					<br/>
					<xsl:text>Pasaport No: </xsl:text>
					<xsl:value-of select="cac:IdentityDocumentReference/cbc:ID"/>
					<br/>
					<xsl:text>Ülkesi: </xsl:text>
					<xsl:for-each select="cbc:NationalityID">
						<xsl:call-template name="Country">
							<xsl:with-param name="CountryType">
								<xsl:value-of select="."/>
							</xsl:with-param>
						</xsl:call-template>
					</xsl:for-each>
				</xsl:if>
			</xsl:for-each>
		</td>
	</xsl:template>
	<xsl:template name="Party_Adress" >
		<xsl:param name="PartyType" />
		<td style="width:469px; " align="left">
			<xsl:for-each select="cac:PostalAddress">
				<xsl:for-each select="cbc:StreetName">
					<xsl:apply-templates/>
					<xsl:text>&#160;</xsl:text>
				</xsl:for-each>
				<xsl:for-each select="cbc:BuildingName">
					<xsl:apply-templates/>
				</xsl:for-each>
				<xsl:for-each select="cbc:BuildingNumber">
					<xsl:text> No:</xsl:text>
					<xsl:apply-templates/>
					<xsl:text>&#160;</xsl:text>
				</xsl:for-each>
				<br/>
				<xsl:for-each select="cbc:Room">
					<xsl:text>Kapı No:</xsl:text>
					<xsl:apply-templates/>
					<xsl:text>&#160;</xsl:text>
				</xsl:for-each>
				<br/>
				<xsl:for-each select="cbc:PostalZone">
					<xsl:apply-templates/>
					<xsl:text>&#160;</xsl:text>
				</xsl:for-each>
				<xsl:for-each select="cbc:CitySubdivisionName">
					<xsl:apply-templates/>
					<xsl:text>/ </xsl:text>
				</xsl:for-each>
				<xsl:for-each select="cbc:CityName">
					<xsl:apply-templates/>
					<xsl:text>&#160;</xsl:text>
				</xsl:for-each>
				<xsl:for-each select="cac:Country/cbc:Name">
					<br/>
					<xsl:apply-templates/>
					<br/>
				</xsl:for-each>
			</xsl:for-each>
		</td>
	</xsl:template>
	<xsl:template name="TransportMode">
		<xsl:param name="TransportModeType" />
		<xsl:choose>
			<xsl:when test="$TransportModeType=1">Denizyolu</xsl:when>
			<xsl:when test="$TransportModeType=2">Demiryolu</xsl:when>
			<xsl:when test="$TransportModeType=3">Karayolu</xsl:when>
			<xsl:when test="$TransportModeType=4">Havayolu</xsl:when>
			<xsl:when test="$TransportModeType=5">Posta</xsl:when>
			<xsl:when test="$TransportModeType=6">Çok araçlı</xsl:when>
			<xsl:when test="$TransportModeType=7">Sabit taşıma tesisleri</xsl:when>
			<xsl:when test="$TransportModeType=8">İç su taşımacılığı</xsl:when>
			<xsl:otherwise>
				<xsl:value-of select="$TransportModeType"/>
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>
	<xsl:template name="PaymentMeansCode">
		<xsl:param name="PaymentMeansCodeType" />
		<xsl:choose>
			<xsl:when test="$PaymentMeansCodeType='1'">ODEME ARACISI</xsl:when>
			<xsl:when test="$PaymentMeansCodeType='10'">KAPIDA ODEME</xsl:when>
			<xsl:when test="$PaymentMeansCodeType='30'">EFT/HAVALE</xsl:when>
			<xsl:when test="$PaymentMeansCodeType='48'">KREDIKARTI/BANKAKARTI</xsl:when>
			<xsl:when test="$PaymentMeansCodeType='ZZZ'">Özel Tanımlı</xsl:when>
			<xsl:when test="$PaymentMeansCodeType='97'">DIGER</xsl:when>
			<xsl:otherwise>
				<xsl:value-of select="$PaymentMeansCodeType"/>
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>
	<xsl:template name="Packaging">
		<xsl:param name="PackagingType" />
		<xsl:choose>
			<xsl:when test="$PackagingType='1A'">Çelik bidon</xsl:when>
			<xsl:when test="$PackagingType='1B'">Alüminyum bidon</xsl:when>
			<xsl:when test="$PackagingType='1D'">Kontraplak bidon</xsl:when>
			<xsl:when test="$PackagingType='1F'">Esnek ambalaj kutu</xsl:when>
			<xsl:when test="$PackagingType='1G'">Elyaflı silindir</xsl:when>
			<xsl:when test="$PackagingType='1W'">Ahşap silindir</xsl:when>
			<xsl:when test="$PackagingType='2C'">Ahşap varil</xsl:when>
			<xsl:when test="$PackagingType='3A'">Beş galonluk çelik bidon</xsl:when>
			<xsl:when test="$PackagingType='3H'">Beş galonluk plastik bidon</xsl:when>
			<xsl:when test="$PackagingType='43'">Torba, süper boy</xsl:when>
			<xsl:when test="$PackagingType='44'">Çoklu torba</xsl:when>
			<xsl:when test="$PackagingType='4A'">Çelik kutu</xsl:when>
			<xsl:when test="$PackagingType='4B'">Alüminyum kutu</xsl:when>
			<xsl:when test="$PackagingType='4C'">Doğal ahşap kutu</xsl:when>
			<xsl:when test="$PackagingType='4D'">Kontraplak kutu</xsl:when>
			<xsl:when test="$PackagingType='4F'">Yeniden üretilmiş ahşap kutu</xsl:when>
			<xsl:when test="$PackagingType='4G'">Elyaf tahta kutu</xsl:when>
			<xsl:when test="$PackagingType='4H'">Plastik kutu</xsl:when>
			<xsl:when test="$PackagingType='5H'">Plastik dokuma torba</xsl:when>
			<xsl:when test="$PackagingType='5L'">Kumaş torba</xsl:when>
			<xsl:when test="$PackagingType='5M'">Kağıt torba</xsl:when>
			<xsl:when test="$PackagingType='6H'">Kompozit ambalaj, plastik kap</xsl:when>
			<xsl:when test="$PackagingType='6P'">Kompozit ambalaj, cam kutu</xsl:when>
			<xsl:when test="$PackagingType='7A'">Araba kabı</xsl:when>
			<xsl:when test="$PackagingType='7B'">Ahşap kasa</xsl:when>
			<xsl:when test="$PackagingType='8A'">Ahşap palet</xsl:when>
			<xsl:when test="$PackagingType='8B'">Ahşap kasa</xsl:when>
			<xsl:when test="$PackagingType='8C'">Ahşap paketi</xsl:when>
			<xsl:when test="$PackagingType='AA'">Ortaboy sert plastik dolum konteynerı</xsl:when>
			<xsl:when test="$PackagingType='AB'">Elyaf kap</xsl:when>
			<xsl:when test="$PackagingType='AC'">Kağıt kap</xsl:when>
			<xsl:when test="$PackagingType='AD'">Ahşap kap</xsl:when>
			<xsl:when test="$PackagingType='AE'">Aerosol</xsl:when>
			<xsl:when test="$PackagingType='AF'">Palet, modüler, yaka 80cms * 60cms</xsl:when>
			<xsl:when test="$PackagingType='AG'">Sarılmış palet</xsl:when>
			<xsl:when test="$PackagingType='AH'">Palet, 100 cms * 110 cms</xsl:when>
			<xsl:when test="$PackagingType='AI'">Çift çeneli kepçe</xsl:when>
			<xsl:when test="$PackagingType='AJ'">Koni</xsl:when>
			<xsl:when test="$PackagingType='AL'">Top</xsl:when>
			<xsl:when test="$PackagingType='AM'">Korumasız ampul</xsl:when>
			<xsl:when test="$PackagingType='AP'">Korumalı ampül</xsl:when>
			<xsl:when test="$PackagingType='AT'">Püskürteç</xsl:when>
			<xsl:when test="$PackagingType='AV'">Kapsül</xsl:when>
			<xsl:when test="$PackagingType='B4'">Kemer</xsl:when>
			<xsl:when test="$PackagingType='BA'">Varil</xsl:when>
			<xsl:when test="$PackagingType='BB'">Bobin</xsl:when>
			<xsl:when test="$PackagingType='BC'">Şişe kasası/rafı</xsl:when>
			<xsl:when test="$PackagingType='BD'">Tahta</xsl:when>
			<xsl:when test="$PackagingType='BE'">Bohça</xsl:when>
			<xsl:when test="$PackagingType='BF'">Balon, korunmasız</xsl:when>
			<xsl:when test="$PackagingType='BG'">Torba</xsl:when>
			<xsl:when test="$PackagingType='BH'">Demet</xsl:when>
			<xsl:when test="$PackagingType='BI'">Çöp kutusu</xsl:when>
			<xsl:when test="$PackagingType='BJ'">Kova</xsl:when>
			<xsl:when test="$PackagingType='BK'">Sepet</xsl:when>
			<xsl:when test="$PackagingType='BL'">Sıkıştırılmış balya</xsl:when>
			<xsl:when test="$PackagingType='BM'">Kase</xsl:when>
			<xsl:when test="$PackagingType='BN'">Sıkıştırılmamış balya</xsl:when>
			<xsl:when test="$PackagingType='BO'">Şişe, korunmasız, silindirik</xsl:when>
			<xsl:when test="$PackagingType='BP'">Balon, korunmasız</xsl:when>
			<xsl:when test="$PackagingType='BQ'">Şişe, korunmuş, silindirik</xsl:when>
			<xsl:when test="$PackagingType='BR'">Çubuk</xsl:when>
			<xsl:when test="$PackagingType='BS'">Şişe, korunmasız, soğanbiçim</xsl:when>
			<xsl:when test="$PackagingType='BT'">Sürgü</xsl:when>
			<xsl:when test="$PackagingType='BU'">İzmarit</xsl:when>
			<xsl:when test="$PackagingType='BV'">Şişe, korunmuş, soğanbiçim</xsl:when>
			<xsl:when test="$PackagingType='BW'">Sıvılar için kutu</xsl:when>
			<xsl:when test="$PackagingType='BX'">Kutu</xsl:when>
			<xsl:when test="$PackagingType='BY'">Tahta, paket halinde/demet</xsl:when>
			<xsl:when test="$PackagingType='BZ'">Çıbuklar, paket halinde/demet</xsl:when>
			<xsl:when test="$PackagingType='CA'">Dikdörtgen teneke</xsl:when>
			<xsl:when test="$PackagingType='CB'">Bira kasası</xsl:when>
			<xsl:when test="$PackagingType='CC'">Yayık</xsl:when>
			<xsl:when test="$PackagingType='CD'">Teneke ibrik</xsl:when>
			<xsl:when test="$PackagingType='CE'">Balık sepeti</xsl:when>
			<xsl:when test="$PackagingType='CF'">Sandık</xsl:when>
			<xsl:when test="$PackagingType='CG'">Kafes</xsl:when>
			<xsl:when test="$PackagingType='CH'">Sandık</xsl:when>
			<xsl:when test="$PackagingType='CI'">Teneke kutu</xsl:when>
			<xsl:when test="$PackagingType='CJ'">Tabut</xsl:when>
			<xsl:when test="$PackagingType='CK'">Fıçı</xsl:when>
			<xsl:when test="$PackagingType='CL'">Bobin</xsl:when>
			<xsl:when test="$PackagingType='CM'">Kart</xsl:when>
			<xsl:when test="$PackagingType='CN'">Konteyner</xsl:when>
			<xsl:when test="$PackagingType='CO'">Damacana, korumasız</xsl:when>
			<xsl:when test="$PackagingType='CP'">Damacana, korumalı</xsl:when>
			<xsl:when test="$PackagingType='CQ'">Kartuş</xsl:when>
			<xsl:when test="$PackagingType='CR'">Kasa</xsl:when>
			<xsl:when test="$PackagingType='CS'">Kutu</xsl:when>
			<xsl:when test="$PackagingType='CT'">Karton kutu</xsl:when>
			<xsl:when test="$PackagingType='CU'">Fincan</xsl:when>
			<xsl:when test="$PackagingType='CV'">Kapak</xsl:when>
			<xsl:when test="$PackagingType='CW'">Rulo kafes</xsl:when>
			<xsl:when test="$PackagingType='CX'">Silindirik teneke</xsl:when>
			<xsl:when test="$PackagingType='CY'">Silindir</xsl:when>
			<xsl:when test="$PackagingType='CZ'">Tuval</xsl:when>
			<xsl:when test="$PackagingType='DA'">Kasa, çok tabakalı, plastik</xsl:when>
			<xsl:when test="$PackagingType='DB'">Kasa, çok tabakalı, ahşap</xsl:when>
			<xsl:when test="$PackagingType='DC'">Kasa, çok tabakalı, karton</xsl:when>
			<xsl:when test="$PackagingType='DI'">Demir varil</xsl:when>
			<xsl:when test="$PackagingType='DJ'">Damacana</xsl:when>
			<xsl:when test="$PackagingType='DK'">Karton kasa</xsl:when>
			<xsl:when test="$PackagingType='DL'">Plastik dökme kasa</xsl:when>
			<xsl:when test="$PackagingType='DM'">Ahşap dökme kasa</xsl:when>
			<xsl:when test="$PackagingType='DN'">Sebil/dağıtıcı</xsl:when>
			<xsl:when test="$PackagingType='DP'">Damacana, korumalı</xsl:when>
			<xsl:when test="$PackagingType='DR'">Bidon</xsl:when>
			<xsl:when test="$PackagingType='DS'">Üst kapaksız plastik tepsi, tek tabaka</xsl:when>
			<xsl:when test="$PackagingType='DT'">Üst kapaksız ahşap tepsi, tek tabaka</xsl:when>
			<xsl:when test="$PackagingType='DU'">Üst kapaksız polistiren tepsi, tek
				tabaka</xsl:when>
			<xsl:when test="$PackagingType='DV'">Üst kapaksız karton tepsi, tek tabaka</xsl:when>
			<xsl:when test="$PackagingType='DW'">Üst kapaksız plastik tepsi, çift tabaka</xsl:when>
			<xsl:when test="$PackagingType='DX'"/>
			<xsl:when test="$PackagingType='DY'">Üst kapaksız karton tepsi, çift tabaka</xsl:when>
			<xsl:when test="$PackagingType='EC'">Plastik torba</xsl:when>
			<xsl:when test="$PackagingType='ED'">Kasa, palet tabanı ile</xsl:when>
			<xsl:when test="$PackagingType='EE'">Ahşap kasa, palet tabanı ile</xsl:when>
			<xsl:when test="$PackagingType='EF'">Karton kasa, palet tabanı ile</xsl:when>
			<xsl:when test="$PackagingType='EG'">Plastik kasa, palet tabanı ile</xsl:when>
			<xsl:when test="$PackagingType='EH'">Metal kasa, palet tabanı ile</xsl:when>
			<xsl:when test="$PackagingType='EI'">İzotermik kasa</xsl:when>
			<xsl:when test="$PackagingType='EN'">Zarf</xsl:when>
			<xsl:when test="$PackagingType='FB'">Plastik esnek torba</xsl:when>
			<xsl:when test="$PackagingType='FC'">Meyve kasası</xsl:when>
			<xsl:when test="$PackagingType='FD'">Çerçeveli kasa</xsl:when>
			<xsl:when test="$PackagingType='FE'">Plastik esnek depo</xsl:when>
			<xsl:when test="$PackagingType='FI'">Küçük fıçı</xsl:when>
			<xsl:when test="$PackagingType='FL'">Matara</xsl:when>
			<xsl:when test="$PackagingType='FO'">Küçük sandık</xsl:when>
			<xsl:when test="$PackagingType='FR'">Çerçeve</xsl:when>
			<xsl:when test="$PackagingType='FT'">Streçlenmiş yemek kabı</xsl:when>
			<xsl:when test="$PackagingType='FW'">Yanları üstü açık yük arabası</xsl:when>
			<xsl:when test="$PackagingType='FX'">Esnek torba</xsl:when>
			<xsl:when test="$PackagingType='GB'">Gaz şişesi</xsl:when>
			<xsl:when test="$PackagingType='GI'">Kiriş</xsl:when>
			<xsl:when test="$PackagingType='GL'">Konteyner, galon</xsl:when>
			<xsl:when test="$PackagingType='GR'">Cam kap</xsl:when>
			<xsl:when test="$PackagingType='GY'">Çul</xsl:when>
			<xsl:when test="$PackagingType='GZ'">Kiriş, demet/grup</xsl:when>
			<xsl:when test="$PackagingType='HA'">Saplı plastik sepet</xsl:when>
			<xsl:when test="$PackagingType='HB'">Saplı ahşap sepet</xsl:when>
			<xsl:when test="$PackagingType='HC'">Saplı karton sepet</xsl:when>
			<xsl:when test="$PackagingType='HG'">Büyük fıçı</xsl:when>
			<xsl:when test="$PackagingType='HN'">Askı</xsl:when>
			<xsl:when test="$PackagingType='HR'">Kapaklı sepet</xsl:when>
			<xsl:when test="$PackagingType='IA'">Ahşap sergi paketi</xsl:when>
			<xsl:when test="$PackagingType='IB'">Karton sergi paketi</xsl:when>
			<xsl:when test="$PackagingType='IC'">Plastik sergi paketi</xsl:when>
			<xsl:when test="$PackagingType='ID'">Metal sergi paketi</xsl:when>
			<xsl:when test="$PackagingType='IE'">Gösteri paketi</xsl:when>
			<xsl:when test="$PackagingType='IF'">Şeffaf oluklu paket</xsl:when>
			<xsl:when test="$PackagingType='IG'">Kağıt sarılı ambalaj</xsl:when>
			<xsl:when test="$PackagingType='IH'">Plastik bidon</xsl:when>
			<xsl:when test="$PackagingType='IK'">Şişe delikli karton paket</xsl:when>
			<xsl:when test="$PackagingType='IL'">Tepsi, katı, kapaklı istiflenebilir</xsl:when>
			<xsl:when test="$PackagingType='IN'">Külçe</xsl:when>
			<xsl:when test="$PackagingType='IZ'">Paket/grop halde külçe</xsl:when>
			<xsl:when test="$PackagingType='JB'">Jumbo boy torba</xsl:when>
			<xsl:when test="$PackagingType='JC'">Beş galonluk dikdörtgen bidon</xsl:when>
			<xsl:when test="$PackagingType='JG'">Sürahi</xsl:when>
			<xsl:when test="$PackagingType='JR'">Kavanoz</xsl:when>
			<xsl:when test="$PackagingType='JY'">Beş galonluk silindir bidon</xsl:when>
			<xsl:when test="$PackagingType='KI'">Takım</xsl:when>
			<xsl:when test="$PackagingType='LE'">Bagaj</xsl:when>
			<xsl:when test="$PackagingType='LG'">Kütük</xsl:when>
			<xsl:when test="$PackagingType='LT'">Pay</xsl:when>
			<xsl:when test="$PackagingType='LU'">Kulp</xsl:when>
			<xsl:when test="$PackagingType='LV'">Liftvan</xsl:when>
			<xsl:when test="$PackagingType='LZ'">Paket/grup kütükler</xsl:when>
			<xsl:when test="$PackagingType='MA'">Metal kasa</xsl:when>
			<xsl:when test="$PackagingType='MB'">Çoklu çanta</xsl:when>
			<xsl:when test="$PackagingType='MC'">Süt kasasu</xsl:when>
			<xsl:when test="$PackagingType='ME'">Metal konteyner</xsl:when>
			<xsl:when test="$PackagingType='MR'">Metal kap</xsl:when>
			<xsl:when test="$PackagingType='MS'">Çok duvarlı çuval</xsl:when>
			<xsl:when test="$PackagingType='MT'">Mat</xsl:when>
			<xsl:when test="$PackagingType='MW'">Plastik sarılmış kap</xsl:when>
			<xsl:when test="$PackagingType='MX'">Kibrit kutusu</xsl:when>
			<xsl:when test="$PackagingType='NE'">Ambalajsız</xsl:when>
			<xsl:when test="$PackagingType='NF'">Ambalajsız, tek ünite</xsl:when>
			<xsl:when test="$PackagingType='NG'">Ambalajsız, çok ünite</xsl:when>
			<xsl:when test="$PackagingType='NS'">Yuva</xsl:when>
			<xsl:when test="$PackagingType='NT'">Ağ</xsl:when>
			<xsl:when test="$PackagingType='NU'">Plastik ağ tüp</xsl:when>
			<xsl:when test="$PackagingType='NV'">Kumaş ağ tüp</xsl:when>
			<xsl:when test="$PackagingType='OA'">Palet, CHEP 40x60 cm</xsl:when>
			<xsl:when test="$PackagingType='OB'">Palet, CHEP 80x120 cm</xsl:when>
			<xsl:when test="$PackagingType='OC'">Palet, CHEP 100x120 cm</xsl:when>
			<xsl:when test="$PackagingType='OD'">Avustralya standart paleti</xsl:when>
			<xsl:when test="$PackagingType='OE'">Palet, 110x100 cm</xsl:when>
			<xsl:when test="$PackagingType='OF'">Nakliye platformu, belirtilmemiş ağırlık ve
				bıyut</xsl:when>
			<xsl:when test="$PackagingType='OK'">Blok</xsl:when>
			<xsl:when test="$PackagingType='OT'">Sekiz kenar kutu</xsl:when>
			<xsl:when test="$PackagingType='OU'">Dış konteyner</xsl:when>
			<xsl:when test="$PackagingType='P2'">Tava</xsl:when>
			<xsl:when test="$PackagingType='PA'">Küçük paket</xsl:when>
			<xsl:when test="$PackagingType='PB'">Kombine açık uçlu kutu ve palet</xsl:when>
			<xsl:when test="$PackagingType='PC'">Parsel</xsl:when>
			<xsl:when test="$PackagingType='PD'">Palet, modüler 80 x 100 cm</xsl:when>
			<xsl:when test="$PackagingType='PE'">Palet, modüler 80 x 120 cm</xsl:when>
			<xsl:when test="$PackagingType='PF'">Kalem</xsl:when>
			<xsl:when test="$PackagingType='PG'">Plaka</xsl:when>
			<xsl:when test="$PackagingType='PH'">Sürahi</xsl:when>
			<xsl:when test="$PackagingType='PI'">Boru</xsl:when>
			<xsl:when test="$PackagingType='PJ'">Meyve sepeti</xsl:when>
			<xsl:when test="$PackagingType='PK'">Paket</xsl:when>
			<xsl:when test="$PackagingType='PL'">Gerdel</xsl:when>
			<xsl:when test="$PackagingType='PN'">Kalas</xsl:when>
			<xsl:when test="$PackagingType='PO'">Destek</xsl:when>
			<xsl:when test="$PackagingType='PP'">Parça</xsl:when>
			<xsl:when test="$PackagingType='PR'">Plastik kap</xsl:when>
			<xsl:when test="$PackagingType='PT'">Demlik</xsl:when>
			<xsl:when test="$PackagingType='PU'">Tepsi</xsl:when>
			<xsl:when test="$PackagingType='PV'">Paket/grup boru</xsl:when>
			<xsl:when test="$PackagingType='PX'">Palet</xsl:when>
			<xsl:when test="$PackagingType='PY'">Paket/grup tabak</xsl:when>
			<xsl:when test="$PackagingType='PZ'">Paket/grup kalas</xsl:when>
			<xsl:when test="$PackagingType='QA'">Üstü açılmaz çelik bidon</xsl:when>
			<xsl:when test="$PackagingType='QB'">Üstü açılır çelik bidon</xsl:when>
			<xsl:when test="$PackagingType='QC'">Üstü açılmaz alüminyum bidon</xsl:when>
			<xsl:when test="$PackagingType='QD'">Üstü açılır alüminyum bidon</xsl:when>
			<xsl:when test="$PackagingType='QF'">Üstü açılmaz plastik bidon</xsl:when>
			<xsl:when test="$PackagingType='QG'">Üstü açılır plastik bidon</xsl:when>
			<xsl:when test="$PackagingType='QH'">Ahşap tıkaçlı varil</xsl:when>
			<xsl:when test="$PackagingType='QJ'">Üstü açılır ahşap varil</xsl:when>
			<xsl:when test="$PackagingType='QK'">Üstü açılmaz beş galonluk çelik bidon</xsl:when>
			<xsl:when test="$PackagingType='QL'">Üstü açılır beş galonluk çelik bidon</xsl:when>
			<xsl:when test="$PackagingType='QM'">Üstü açılmaz beş galonluk plastik bidon</xsl:when>
			<xsl:when test="$PackagingType='QN'">Üstü açılır beş galonluk plastik bidon</xsl:when>
			<xsl:when test="$PackagingType='QP'">Doğal ahşap kutu</xsl:when>
			<xsl:when test="$PackagingType='QQ'">Emniyet duvarlı doğal ahşap kutu</xsl:when>
			<xsl:when test="$PackagingType='QR'">Genişletilmiş plastik kutu</xsl:when>
			<xsl:when test="$PackagingType='QS'">Yekpare plastik kutu</xsl:when>
			<xsl:when test="$PackagingType='RD'">Çubuk</xsl:when>
			<xsl:when test="$PackagingType='RG'">Halka</xsl:when>
			<xsl:when test="$PackagingType='RJ'">Raf, elbise askısı</xsl:when>
			<xsl:when test="$PackagingType='RK'">Raf</xsl:when>
			<xsl:when test="$PackagingType='RL'">Makara</xsl:when>
			<xsl:when test="$PackagingType='RO'">Rulo</xsl:when>
			<xsl:when test="$PackagingType='RZ'">Paket/grup çubuk</xsl:when>
			<xsl:when test="$PackagingType='SA'">Çuval</xsl:when>
			<xsl:when test="$PackagingType='SB'">Levha</xsl:when>
			<xsl:when test="$PackagingType='SC'">Sığ kasa</xsl:when>
			<xsl:when test="$PackagingType='SD'">İğ</xsl:when>
			<xsl:when test="$PackagingType='SE'">Deniz sandığı</xsl:when>
			<xsl:when test="$PackagingType='SH'">Kesecik</xsl:when>
			<xsl:when test="$PackagingType='SI'">Kızak</xsl:when>
			<xsl:when test="$PackagingType='SK'">İskelet kasa</xsl:when>
			<xsl:when test="$PackagingType='SL'">Taşıma paleti</xsl:when>
			<xsl:when test="$PackagingType='SM'">Sac</xsl:when>
			<xsl:when test="$PackagingType='SO'">Tel/kablo/iplik makarası</xsl:when>
			<xsl:when test="$PackagingType='SP'">Plastik levha</xsl:when>
			<xsl:when test="$PackagingType='SS'">Çelik kasa</xsl:when>
			<xsl:when test="$PackagingType='ST'">Yaprak</xsl:when>
			<xsl:when test="$PackagingType='SU'">Bavul</xsl:when>
			<xsl:when test="$PackagingType='SV'">Çelik zarf</xsl:when>
			<xsl:when test="$PackagingType='SW'">Vakumlu ambalaj</xsl:when>
			<xsl:when test="$PackagingType='SX'">Set</xsl:when>
			<xsl:when test="$PackagingType='SY'">Kılıf</xsl:when>
			<xsl:when test="$PackagingType='SZ'">Paket/grup yaprak</xsl:when>
			<xsl:when test="$PackagingType='T1'">Tablet</xsl:when>
			<xsl:when test="$PackagingType='TB'">Küvet</xsl:when>
			<xsl:when test="$PackagingType='TC'">Çay sandığı</xsl:when>
			<xsl:when test="$PackagingType='TD'">Sıkılabilir tüp</xsl:when>
			<xsl:when test="$PackagingType='TE'">Lastik</xsl:when>
			<xsl:when test="$PackagingType='TG'">Genel tank konteynerı</xsl:when>
			<xsl:when test="$PackagingType='TI'"/>
			<xsl:when test="$PackagingType='TK'">Dikdörtgen tank</xsl:when>
			<xsl:when test="$PackagingType='TN'">Teneke</xsl:when>
			<xsl:when test="$PackagingType='TO'">Şarap fıçısı</xsl:when>
			<xsl:when test="$PackagingType='TR'">Gövde</xsl:when>
			<xsl:when test="$PackagingType='TS'">Bağ</xsl:when>
			<xsl:when test="$PackagingType='TU'">Tüp</xsl:when>
			<xsl:when test="$PackagingType='TV'">Enjektörlü tüp</xsl:when>
			<xsl:when test="$PackagingType='TY'">Silindirik tank</xsl:when>
			<xsl:when test="$PackagingType='TZ'">Paket/grup tüpler</xsl:when>
			<xsl:when test="$PackagingType='UN'">Birim</xsl:when>
			<xsl:when test="$PackagingType='VG'">Dökme gaz</xsl:when>
			<xsl:when test="$PackagingType='VI'">Küçük şişe</xsl:when>
			<xsl:when test="$PackagingType='VL'">Dökme sıvı</xsl:when>
			<xsl:when test="$PackagingType='VO'">Dökme katı</xsl:when>
			<xsl:when test="$PackagingType='VP'">Vakumlu</xsl:when>
			<xsl:when test="$PackagingType='VQ'">Dökme sıvılaştırılmış gaz</xsl:when>
			<xsl:when test="$PackagingType='VN'">Araç</xsl:when>
			<xsl:when test="$PackagingType='VR'">Dökme katı granül</xsl:when>
			<xsl:when test="$PackagingType='VS'">Dökme metal hurda</xsl:when>
			<xsl:when test="$PackagingType='VY'">Dökme ince parçacıklar</xsl:when>
			<xsl:when test="$PackagingType='WA'">Ortaboy dolum konteynerı</xsl:when>
			<xsl:when test="$PackagingType='WB'">Hasırlı şişe</xsl:when>
			<xsl:when test="$PackagingType='WC'">Ortaboy çelik dolum konteynerı</xsl:when>
			<xsl:when test="$PackagingType='WD'">Ortaboy alüminyum dolum konteynerı</xsl:when>
			<xsl:when test="$PackagingType='WF'">Ortaboy metal dolum konteynerı</xsl:when>
			<xsl:when test="$PackagingType='WK'">Sıvılar için ortaboy çelik dolum
				konteynerı</xsl:when>
			<xsl:when test="$PackagingType='WL'">Sıvılar için ortaboy alümünyum dolum
				konteynerı</xsl:when>
			<xsl:when test="$PackagingType='WM'">Sıvılar için ortaboy metal dolum
				konteynerı</xsl:when>
			<xsl:when test="$PackagingType='WN'">Ortaboy iç astarsız örme plastik dolum
				konteynerı</xsl:when>
			<xsl:when test="$PackagingType='WR'">Ortaboy iç astarlı örme plastik dolum
				konteynerı</xsl:when>
			<xsl:when test="$PackagingType='WS'">Ortaboy plastik film dolum konteynerı</xsl:when>
			<xsl:when test="$PackagingType='WT'">Ortaboy iç astarsız kumaş plastik dolum
				konteynerı</xsl:when>
			<xsl:when test="$PackagingType='WU'">Ortaboy iç astarlı doğal ahşap dolum
				konteynerı</xsl:when>
			<xsl:when test="$PackagingType='WX'">Ortaboy iç astarlı kumaş dolum
				konteynerı</xsl:when>
			<xsl:when test="$PackagingType='WY'">Ortaboy iç astarlı kontraplak dolum
				konteynerı</xsl:when>
			<xsl:when test="$PackagingType='WZ'">Ortaboy iç astarlı sunta dolum
				konteynerı</xsl:when>
			<xsl:when test="$PackagingType='XA'">İç astarsız örme plastik torba</xsl:when>
			<xsl:when test="$PackagingType='XB'">Sızdırmaz örme plastik torba</xsl:when>
			<xsl:when test="$PackagingType='XC'">Su geçirmez örme plastik torba</xsl:when>
			<xsl:when test="$PackagingType='XD'">Plastik film torba</xsl:when>
			<xsl:when test="$PackagingType='XF'">İç astarsız kumaş torba</xsl:when>
			<xsl:when test="$PackagingType='XG'">Sızdırmaz kumaş torba</xsl:when>
			<xsl:when test="$PackagingType='XH'">Su geçirmez kumaş torba</xsl:when>
			<xsl:when test="$PackagingType='XJ'">Çok duvarlı kağıt torba</xsl:when>
			<xsl:when test="$PackagingType='XK'">Su geçirmez çok duvarlı kağıt torba</xsl:when>
			<xsl:when test="$PackagingType='YA'">Kompozit ambalaj, çelik bidon içindeki plastik
				kap</xsl:when>
			<xsl:when test="$PackagingType='YB'">Kompozit ambalaj, çelik kasa içindeki plastik
				kap</xsl:when>
			<xsl:when test="$PackagingType='YC'">Kompozit ambalaj, alüminyum bidon içindeki plastik
				kap</xsl:when>
			<xsl:when test="$PackagingType='YD'">Kompozit ambalaj, alüminyum kasa içindeki plastik
				kap</xsl:when>
			<xsl:when test="$PackagingType='YF'">Kompozit ambalaj, ahşap kutu içindeki plastik
				kap</xsl:when>
			<xsl:when test="$PackagingType='YG'">Kompozit ambalaj, kontraplak bidon içindeki plastik
				kap</xsl:when>
			<xsl:when test="$PackagingType='YH'">Kompozit ambalaj, kontraplak kasa içindeki plastik
				kap</xsl:when>
			<xsl:when test="$PackagingType='YJ'">Kompozit ambalaj, elyaf bidon içindeki plastik
				kap</xsl:when>
			<xsl:when test="$PackagingType='YK'">Kompozit ambalaj, elyaf levha kasa içindeki plastik
				kap</xsl:when>
			<xsl:when test="$PackagingType='YL'">Kompozit ambalaj, plastik bidon içindeki plastik
				kap</xsl:when>
			<xsl:when test="$PackagingType='YM'">Kompozit ambalaj, yekpare plastik kasa içindeki
				plastik kap</xsl:when>
			<xsl:when test="$PackagingType='YN'">Kompozit ambalaj, çelik bidon içindeki cam
				kap</xsl:when>
			<xsl:when test="$PackagingType='YP'">Kompozit ambalaj, elyaf levha kasa içindeki plastik
				kap</xsl:when>
			<xsl:when test="$PackagingType='YQ'">Kompozit ambalaj, alüminyum bidon içindeki cam
				kap</xsl:when>
			<xsl:when test="$PackagingType='YR'">Kompozit ambalaj, alüminyum kasa içindeki plastik
				kap</xsl:when>
			<xsl:when test="$PackagingType='YS'">Kompozit ambalaj, ahşap kasa içindeki cam
				kap</xsl:when>
			<xsl:when test="$PackagingType='YT'">Kompozit ambalaj, kontraplak bidon içindeki cam
				kap</xsl:when>
			<xsl:when test="$PackagingType='YV'">Kompozit ambalaj, hasır sepet içindeki cam
				kap</xsl:when>
			<xsl:when test="$PackagingType='YW'">Kompozit ambalaj, elyaf bidon içindeki cam
				kap</xsl:when>
			<xsl:when test="$PackagingType='YX'">Kompozit ambalaj, elyaf levha kasa içindeki cam
				kap</xsl:when>
			<xsl:when test="$PackagingType='YY'">Kompozit ambalaj, genişleyebilir plastik paket
				içindeki cam kap</xsl:when>
			<xsl:when test="$PackagingType='YZ'">Kompozit ambalaj, yekpare plastik paket içindeki
				cam kap</xsl:when>
			<xsl:when test="$PackagingType='ZA'">Ortaboy çok duvarlı kağıt dolum
				konteynerı</xsl:when>
			<xsl:when test="$PackagingType='ZB'">Büyük boy torba</xsl:when>
			<xsl:when test="$PackagingType='ZC'">Ortaboy çok duvarlı su geçirmez kağıt dolum
				konteynerı</xsl:when>
			<xsl:when test="$PackagingType='ZL'">Ortaboy kompozit yekpare sert plastik dolum
				konteynerı</xsl:when>
			<xsl:when test="$PackagingType='ZM'">Ortaboy kompozit yekpare esnek plastik dolum
				konteynerı</xsl:when>
			<xsl:when test="$PackagingType='ZN'">Ortaboy kompozit sıkıştırılmış sert plastik dolum
				konteynerı</xsl:when>
			<xsl:when test="$PackagingType='ZP'">Ortaboy kompozit sıkıştırılmış esnek plastik dolum
				konteynerı</xsl:when>
			<xsl:when test="$PackagingType='ZQ'">Sıvılar için ortaboy kompozit sert plastik dolum
				konteynerı</xsl:when>
			<xsl:when test="$PackagingType='ZR'">Sıvılar için ortaboy kompozit esnek plastik dolum
				konteynerı</xsl:when>
			<xsl:when test="$PackagingType='ZS'">Ortaboy kompozit dolum konteynerı</xsl:when>
			<xsl:when test="$PackagingType='ZT'">Ortaboy elyaf levha dolum konteynerı</xsl:when>
			<xsl:when test="$PackagingType='ZU'">Ortaboy esnek dolum konteynerı</xsl:when>
			<xsl:when test="$PackagingType='ZW'">Ortaboy doğal ahşap dolum konteynerı</xsl:when>
			<xsl:when test="$PackagingType='ZX'">Ortaboy kontraplak dolum konteynerı</xsl:when>
			<xsl:when test="$PackagingType='ZY'">Ortaboy sunta dolum konteynerı</xsl:when>
			<xsl:otherwise>
				<xsl:value-of select="$PackagingType"/>
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>
	<xsl:template name="Country">
		<xsl:param name="CountryType" />
		<xsl:choose>
			<xsl:when test="$CountryType='AF'">Afganistan</xsl:when>
			<xsl:when test="$CountryType='DE'">Almanya</xsl:when>
			<xsl:when test="$CountryType='AD'">Andorra</xsl:when>
			<xsl:when test="$CountryType='AO'">Angola</xsl:when>
			<xsl:when test="$CountryType='AG'">Antigua ve Barbuda</xsl:when>
			<xsl:when test="$CountryType='AR'">Arjantin</xsl:when>
			<xsl:when test="$CountryType='AL'">Arnavutluk</xsl:when>
			<xsl:when test="$CountryType='AW'">Aruba</xsl:when>
			<xsl:when test="$CountryType='AU'">Avustralya</xsl:when>
			<xsl:when test="$CountryType='AT'">Avusturya</xsl:when>
			<xsl:when test="$CountryType='AZ'">Azerbaycan</xsl:when>
			<xsl:when test="$CountryType='BS'">Bahamalar</xsl:when>
			<xsl:when test="$CountryType='BH'">Bahreyn</xsl:when>
			<xsl:when test="$CountryType='BD'">Bangladeş</xsl:when>
			<xsl:when test="$CountryType='BB'">Barbados</xsl:when>
			<xsl:when test="$CountryType='EH'">Batı Sahra (MA)</xsl:when>
			<xsl:when test="$CountryType='BE'">Belçika</xsl:when>
			<xsl:when test="$CountryType='BZ'">Belize</xsl:when>
			<xsl:when test="$CountryType='BJ'">Benin</xsl:when>
			<xsl:when test="$CountryType='BM'">Bermuda</xsl:when>
			<xsl:when test="$CountryType='BY'">Beyaz Rusya</xsl:when>
			<xsl:when test="$CountryType='BT'">Bhutan</xsl:when>
			<xsl:when test="$CountryType='AE'">Birleşik Arap Emirlikleri</xsl:when>
			<xsl:when test="$CountryType='US'">Birleşik Devletler</xsl:when>
			<xsl:when test="$CountryType='GB'">Birleşik Krallık</xsl:when>
			<xsl:when test="$CountryType='BO'">Bolivya</xsl:when>
			<xsl:when test="$CountryType='BA'">Bosna-Hersek</xsl:when>
			<xsl:when test="$CountryType='BW'">Botsvana</xsl:when>
			<xsl:when test="$CountryType='BR'">Brezilya</xsl:when>
			<xsl:when test="$CountryType='BN'">Bruney</xsl:when>
			<xsl:when test="$CountryType='BG'">Bulgaristan</xsl:when>
			<xsl:when test="$CountryType='BF'">Burkina Faso</xsl:when>
			<xsl:when test="$CountryType='BI'">Burundi</xsl:when>
			<xsl:when test="$CountryType='TD'">Çad</xsl:when>
			<xsl:when test="$CountryType='KY'">Cayman Adaları</xsl:when>
			<xsl:when test="$CountryType='GI'">Cebelitarık (GB)</xsl:when>
			<xsl:when test="$CountryType='CZ'">Çek Cumhuriyeti</xsl:when>
			<xsl:when test="$CountryType='DZ'">Cezayir</xsl:when>
			<xsl:when test="$CountryType='DJ'">Cibuti</xsl:when>
			<xsl:when test="$CountryType='CN'">Çin</xsl:when>
			<xsl:when test="$CountryType='DK'">Danimarka</xsl:when>
			<xsl:when test="$CountryType='CD'">Demokratik Kongo Cumhuriyeti</xsl:when>
			<xsl:when test="$CountryType='TL'">Doğu Timor</xsl:when>
			<xsl:when test="$CountryType='DO'">Dominik Cumhuriyeti</xsl:when>
			<xsl:when test="$CountryType='DM'">Dominika</xsl:when>
			<xsl:when test="$CountryType='EC'">Ekvador</xsl:when>
			<xsl:when test="$CountryType='GQ'">Ekvator Ginesi</xsl:when>
			<xsl:when test="$CountryType='SV'">El Salvador</xsl:when>
			<xsl:when test="$CountryType='ID'">Endonezya</xsl:when>
			<xsl:when test="$CountryType='ER'">Eritre</xsl:when>
			<xsl:when test="$CountryType='AM'">Ermenistan</xsl:when>
			<xsl:when test="$CountryType='MF'">Ermiş Martin (FR)</xsl:when>
			<xsl:when test="$CountryType='EE'">Estonya</xsl:when>
			<xsl:when test="$CountryType='ET'">Etiyopya</xsl:when>
			<xsl:when test="$CountryType='FK'">Falkland Adaları</xsl:when>
			<xsl:when test="$CountryType='FO'">Faroe Adaları (DK)</xsl:when>
			<xsl:when test="$CountryType='MA'">Fas</xsl:when>
			<xsl:when test="$CountryType='FJ'">Fiji</xsl:when>
			<xsl:when test="$CountryType='CI'">Fildişi Sahili</xsl:when>
			<xsl:when test="$CountryType='PH'">Filipinler</xsl:when>
			<xsl:when test="$CountryType='FI'">Finlandiya</xsl:when>
			<xsl:when test="$CountryType='FR'">Fransa</xsl:when>
			<xsl:when test="$CountryType='GF'">Fransız Guyanası (FR)</xsl:when>
			<xsl:when test="$CountryType='PF'">Fransız Polinezyası (FR)</xsl:when>
			<xsl:when test="$CountryType='GA'">Gabon</xsl:when>
			<xsl:when test="$CountryType='GM'">Gambiya</xsl:when>
			<xsl:when test="$CountryType='GH'">Gana</xsl:when>
			<xsl:when test="$CountryType='GN'">Gine</xsl:when>
			<xsl:when test="$CountryType='GW'">Gine Bissau</xsl:when>
			<xsl:when test="$CountryType='GD'">Grenada</xsl:when>
			<xsl:when test="$CountryType='GL'">Grönland (DK)</xsl:when>
			<xsl:when test="$CountryType='GP'">Guadeloupe (FR)</xsl:when>
			<xsl:when test="$CountryType='GT'">Guatemala</xsl:when>
			<xsl:when test="$CountryType='GG'">Guernsey (GB)</xsl:when>
			<xsl:when test="$CountryType='ZA'">Güney Afrika</xsl:when>
			<xsl:when test="$CountryType='KR'">Güney Kore</xsl:when>
			<xsl:when test="$CountryType='GE'">Gürcistan</xsl:when>
			<xsl:when test="$CountryType='GY'">Guyana</xsl:when>
			<xsl:when test="$CountryType='HT'">Haiti</xsl:when>
			<xsl:when test="$CountryType='IN'">Hindistan</xsl:when>
			<xsl:when test="$CountryType='HR'">Hırvatistan</xsl:when>
			<xsl:when test="$CountryType='NL'">Hollanda</xsl:when>
			<xsl:when test="$CountryType='HN'">Honduras</xsl:when>
			<xsl:when test="$CountryType='HK'">Hong Kong (CN)</xsl:when>
			<xsl:when test="$CountryType='VG'">İngiliz Virjin Adaları</xsl:when>
			<xsl:when test="$CountryType='IQ'">Irak</xsl:when>
			<xsl:when test="$CountryType='IR'">İran</xsl:when>
			<xsl:when test="$CountryType='IE'">İrlanda</xsl:when>
			<xsl:when test="$CountryType='ES'">İspanya</xsl:when>
			<xsl:when test="$CountryType='IL'">İsrail</xsl:when>
			<xsl:when test="$CountryType='SE'">İsveç</xsl:when>
			<xsl:when test="$CountryType='CH'">İsviçre</xsl:when>
			<xsl:when test="$CountryType='IT'">İtalya</xsl:when>
			<xsl:when test="$CountryType='IS'">İzlanda</xsl:when>
			<xsl:when test="$CountryType='JM'">Jamaika</xsl:when>
			<xsl:when test="$CountryType='JP'">Japonya</xsl:when>
			<xsl:when test="$CountryType='JE'">Jersey (GB)</xsl:when>
			<xsl:when test="$CountryType='KH'">Kamboçya</xsl:when>
			<xsl:when test="$CountryType='CM'">Kamerun</xsl:when>
			<xsl:when test="$CountryType='CA'">Kanada</xsl:when>
			<xsl:when test="$CountryType='ME'">Karadağ</xsl:when>
			<xsl:when test="$CountryType='QA'">Katar</xsl:when>
			<xsl:when test="$CountryType='KZ'">Kazakistan</xsl:when>
			<xsl:when test="$CountryType='KE'">Kenya</xsl:when>
			<xsl:when test="$CountryType='CY'">Kıbrıs</xsl:when>
			<xsl:when test="$CountryType='KG'">Kırgızistan</xsl:when>
			<xsl:when test="$CountryType='KI'">Kiribati</xsl:when>
			<xsl:when test="$CountryType='CO'">Kolombiya</xsl:when>
			<xsl:when test="$CountryType='KM'">Komorlar</xsl:when>
			<xsl:when test="$CountryType='CG'">Kongo Cumhuriyeti</xsl:when>
			<xsl:when test="$CountryType='KV'">Kosova (RS)</xsl:when>
			<xsl:when test="$CountryType='CR'">Kosta Rika</xsl:when>
			<xsl:when test="$CountryType='CU'">Küba</xsl:when>
			<xsl:when test="$CountryType='KW'">Kuveyt</xsl:when>
			<xsl:when test="$CountryType='KP'">Kuzey Kore</xsl:when>
			<xsl:when test="$CountryType='LA'">Laos</xsl:when>
			<xsl:when test="$CountryType='LS'">Lesoto</xsl:when>
			<xsl:when test="$CountryType='LV'">Letonya</xsl:when>
			<xsl:when test="$CountryType='LR'">Liberya</xsl:when>
			<xsl:when test="$CountryType='LY'">Libya</xsl:when>
			<xsl:when test="$CountryType='LI'">Lihtenştayn</xsl:when>
			<xsl:when test="$CountryType='LT'">Litvanya</xsl:when>
			<xsl:when test="$CountryType='LB'">Lübnan</xsl:when>
			<xsl:when test="$CountryType='LU'">Lüksemburg</xsl:when>
			<xsl:when test="$CountryType='HU'">Macaristan</xsl:when>
			<xsl:when test="$CountryType='MG'">Madagaskar</xsl:when>
			<xsl:when test="$CountryType='MO'">Makao (CN)</xsl:when>
			<xsl:when test="$CountryType='MK'">Makedonya</xsl:when>
			<xsl:when test="$CountryType='MW'">Malavi</xsl:when>
			<xsl:when test="$CountryType='MV'">Maldivler</xsl:when>
			<xsl:when test="$CountryType='MY'">Malezya</xsl:when>
			<xsl:when test="$CountryType='ML'">Mali</xsl:when>
			<xsl:when test="$CountryType='MT'">Malta</xsl:when>
			<xsl:when test="$CountryType='IM'">Man Adası (GB)</xsl:when>
			<xsl:when test="$CountryType='MH'">Marshall Adaları</xsl:when>
			<xsl:when test="$CountryType='MQ'">Martinique (FR)</xsl:when>
			<xsl:when test="$CountryType='MU'">Mauritius</xsl:when>
			<xsl:when test="$CountryType='YT'">Mayotte (FR)</xsl:when>
			<xsl:when test="$CountryType='MX'">Meksika</xsl:when>
			<xsl:when test="$CountryType='FM'">Mikronezya</xsl:when>
			<xsl:when test="$CountryType='EG'">Mısır</xsl:when>
			<xsl:when test="$CountryType='MN'">Moğolistan</xsl:when>
			<xsl:when test="$CountryType='MD'">Moldova</xsl:when>
			<xsl:when test="$CountryType='MC'">Monako</xsl:when>
			<xsl:when test="$CountryType='MR'">Moritanya</xsl:when>
			<xsl:when test="$CountryType='MZ'">Mozambik</xsl:when>
			<xsl:when test="$CountryType='MM'">Myanmar</xsl:when>
			<xsl:when test="$CountryType='NA'">Namibya</xsl:when>
			<xsl:when test="$CountryType='NR'">Nauru</xsl:when>
			<xsl:when test="$CountryType='NP'">Nepal</xsl:when>
			<xsl:when test="$CountryType='NE'">Nijer</xsl:when>
			<xsl:when test="$CountryType='NG'">Nijerya</xsl:when>
			<xsl:when test="$CountryType='NI'">Nikaragua</xsl:when>
			<xsl:when test="$CountryType='NO'">Norveç</xsl:when>
			<xsl:when test="$CountryType='CF'">Orta Afrika Cumhuriyeti</xsl:when>
			<xsl:when test="$CountryType='UZ'">Özbekistan</xsl:when>
			<xsl:when test="$CountryType='PK'">Pakistan</xsl:when>
			<xsl:when test="$CountryType='PW'">Palau</xsl:when>
			<xsl:when test="$CountryType='PA'">Panama</xsl:when>
			<xsl:when test="$CountryType='PG'">Papua Yeni Gine</xsl:when>
			<xsl:when test="$CountryType='PY'">Paraguay</xsl:when>
			<xsl:when test="$CountryType='PE'">Peru</xsl:when>
			<xsl:when test="$CountryType='PL'">Polonya</xsl:when>
			<xsl:when test="$CountryType='PT'">Portekiz</xsl:when>
			<xsl:when test="$CountryType='PR'">Porto Riko (US)</xsl:when>
			<xsl:when test="$CountryType='RE'">Réunion (FR)</xsl:when>
			<xsl:when test="$CountryType='RO'">Romanya</xsl:when>
			<xsl:when test="$CountryType='RW'">Ruanda</xsl:when>
			<xsl:when test="$CountryType='RU'">Rusya</xsl:when>
			<xsl:when test="$CountryType='BL'">Saint Barthélemy (FR)</xsl:when>
			<xsl:when test="$CountryType='KN'">Saint Kitts ve Nevis</xsl:when>
			<xsl:when test="$CountryType='LC'">Saint Lucia</xsl:when>
			<xsl:when test="$CountryType='PM'">Saint Pierre ve Miquelon (FR)</xsl:when>
			<xsl:when test="$CountryType='VC'">Saint Vincent ve Grenadinler</xsl:when>
			<xsl:when test="$CountryType='WS'">Samoa</xsl:when>
			<xsl:when test="$CountryType='SM'">San Marino</xsl:when>
			<xsl:when test="$CountryType='ST'">São Tomé ve Príncipe</xsl:when>
			<xsl:when test="$CountryType='SN'">Senegal</xsl:when>
			<xsl:when test="$CountryType='SC'">Seyşeller</xsl:when>
			<xsl:when test="$CountryType='SL'">Sierra Leone</xsl:when>
			<xsl:when test="$CountryType='CL'">Şili</xsl:when>
			<xsl:when test="$CountryType='SG'">Singapur</xsl:when>
			<xsl:when test="$CountryType='RS'">Sırbistan</xsl:when>
			<xsl:when test="$CountryType='SK'">Slovakya Cumhuriyeti</xsl:when>
			<xsl:when test="$CountryType='SI'">Slovenya</xsl:when>
			<xsl:when test="$CountryType='SB'">Solomon Adaları</xsl:when>
			<xsl:when test="$CountryType='SO'">Somali</xsl:when>
			<xsl:when test="$CountryType='SS'">South Sudan</xsl:when>
			<xsl:when test="$CountryType='SJ'">Spitsbergen (NO)</xsl:when>
			<xsl:when test="$CountryType='LK'">Sri Lanka</xsl:when>
			<xsl:when test="$CountryType='SD'">Sudan</xsl:when>
			<xsl:when test="$CountryType='SR'">Surinam</xsl:when>
			<xsl:when test="$CountryType='SY'">Suriye</xsl:when>
			<xsl:when test="$CountryType='SA'">Suudi Arabistan</xsl:when>
			<xsl:when test="$CountryType='SZ'">Svaziland</xsl:when>
			<xsl:when test="$CountryType='TJ'">Tacikistan</xsl:when>
			<xsl:when test="$CountryType='TZ'">Tanzanya</xsl:when>
			<xsl:when test="$CountryType='TH'">Tayland</xsl:when>
			<xsl:when test="$CountryType='TW'">Tayvan</xsl:when>
			<xsl:when test="$CountryType='TG'">Togo</xsl:when>
			<xsl:when test="$CountryType='TO'">Tonga</xsl:when>
			<xsl:when test="$CountryType='TT'">Trinidad ve Tobago</xsl:when>
			<xsl:when test="$CountryType='TN'">Tunus</xsl:when>
			<xsl:when test="$CountryType='TR'">Türkiye</xsl:when>
			<xsl:when test="$CountryType='TM'">Türkmenistan</xsl:when>
			<xsl:when test="$CountryType='TC'">Turks ve Caicos</xsl:when>
			<xsl:when test="$CountryType='TV'">Tuvalu</xsl:when>
			<xsl:when test="$CountryType='UG'">Uganda</xsl:when>
			<xsl:when test="$CountryType='UA'">Ukrayna</xsl:when>
			<xsl:when test="$CountryType='OM'">Umman</xsl:when>
			<xsl:when test="$CountryType='JO'">Ürdün</xsl:when>
			<xsl:when test="$CountryType='UY'">Uruguay</xsl:when>
			<xsl:when test="$CountryType='VU'">Vanuatu</xsl:when>
			<xsl:when test="$CountryType='VA'">Vatikan</xsl:when>
			<xsl:when test="$CountryType='VE'">Venezuela</xsl:when>
			<xsl:when test="$CountryType='VN'">Vietnam</xsl:when>
			<xsl:when test="$CountryType='WF'">Wallis ve Futuna (FR)</xsl:when>
			<xsl:when test="$CountryType='YE'">Yemen</xsl:when>
			<xsl:when test="$CountryType='NC'">Yeni Kaledonya (FR)</xsl:when>
			<xsl:when test="$CountryType='NZ'">Yeni Zelanda</xsl:when>
			<xsl:when test="$CountryType='CV'">Yeşil Burun Adaları</xsl:when>
			<xsl:when test="$CountryType='GR'">Yunanistan</xsl:when>
			<xsl:when test="$CountryType='ZM'">Zambiya</xsl:when>
			<xsl:when test="$CountryType='ZW'">Zimbabve</xsl:when>
			<xsl:otherwise>
				<xsl:value-of select="$CountryType"/>
			</xsl:otherwise>
		</xsl:choose>

	</xsl:template>
	<xsl:template name='Party_Other'>
		<xsl:param name="PartyType" />
		<xsl:for-each select="cbc:WebsiteURI">
			<tr align="left">
				<td>
					<xsl:text>Web Sitesi: </xsl:text>
					<xsl:value-of select="."/>
				</td>
			</tr>
		</xsl:for-each>
		<xsl:for-each select="cac:Contact/cbc:ElectronicMail">
			<tr align="left">
				<td>
					<xsl:text>E-Posta: </xsl:text>
					<xsl:value-of select="."/>
				</td>
			</tr>
		</xsl:for-each>
		<xsl:for-each select="cac:Contact">
			<xsl:if test="cbc:Telephone or cbc:Telefax">
				<tr align="left">
					<td style="width:469px; " align="left">
						<xsl:for-each select="cbc:Telephone">
							<xsl:text>Tel: </xsl:text>
							<xsl:apply-templates/>
						</xsl:for-each>
						<xsl:for-each select="cbc:Telefax">
							<xsl:text> Fax: </xsl:text>
							<xsl:apply-templates/>
						</xsl:for-each>
						<xsl:text>&#160;</xsl:text>
					</td>
				</tr>
			</xsl:if>
		</xsl:for-each>
		<xsl:if test="$PartyType!='TAXFREE' and not(starts-with($PartyType, 'EXPORT'))">
			<xsl:for-each select="cac:PartyTaxScheme/cac:TaxScheme/cbc:Name">
				<tr align="left">
					<td>
						<xsl:text>Vergi Dairesi: </xsl:text>
						<xsl:apply-templates/>
					</td>
				</tr>
			</xsl:for-each>
			<xsl:for-each select="cac:PartyIdentification">
				<tr align="left">
					<td>
						<xsl:value-of select="cbc:ID/@schemeID"/>
						<xsl:text>: </xsl:text>
						<xsl:value-of select="cbc:ID"/>
					</td>
				</tr>
			</xsl:for-each>
			<xsl:for-each select="cac:AgentParty/cac:PartyIdentification">
				<tr align="left">
					<td>
						<xsl:value-of select="cbc:ID/@schemeID"/>
						<xsl:text>: </xsl:text>
						<xsl:value-of select="cbc:ID"/>
					</td>
				</tr>
			</xsl:for-each>
		</xsl:if>
	</xsl:template>
	<xsl:template name="Curr_Type">
		<xsl:value-of select="format-number(., '###.##0,00', 'european')"/>
		<xsl:if	test="@currencyID">
			<xsl:text> </xsl:text>
			<xsl:choose>
				<xsl:when test="@currencyID = 'TRL' or @currencyID = 'TRY'">
					<xsl:text>TL</xsl:text>
				</xsl:when>
				<xsl:otherwise>
					<xsl:value-of select="@currencyID"/>
				</xsl:otherwise>
			</xsl:choose>
		</xsl:if>
	</xsl:template>
</xsl:stylesheet>