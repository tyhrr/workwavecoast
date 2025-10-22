"""
Application Service
Business logic for application management
"""
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone
from flask import current_app
from bson import ObjectId
from pymongo.errors import DuplicateKeyError
import re

from services.base_service import BaseService
from models.application import Application
from schemas.basic_schemas import ApplicationCreateSchemaBasic
from config.database import get_database
from config.constants import (
    REQUIRED_FIELDS, VALIDATION_PATTERNS, PHONE_PATTERNS,
    FILE_SIZE_LIMITS, ALLOWED_EXTENSIONS
)


class ApplicationService(BaseService):
    """Service for handling application business logic"""

    def __init__(self, logger: Optional[logging.Logger] = None):
        super().__init__(logger)
        self.db = None
        self.collection = None
        self._initialized = False

    def initialize(self):
        """Initialize database connection"""
        try:
            self.db = get_database()
            self.collection = self.db['candidates']
            self._initialized = True
            self.log_operation("initialize", {"status": "database_connected"})
        except Exception as e:
            self.logger.error(f"Failed to initialize database: {e}")
            raise

    def _ensure_initialized(self):
        """Ensure database is initialized"""
        if not self._initialized:
            self.initialize()

    def validate_phone_number(self, phone: str) -> Tuple[bool, str]:
        """Validate phone number format according to country code"""
        if not phone or not isinstance(phone, str):
            return False, "Número de teléfono requerido"

        phone = phone.strip()

        # Check if phone matches the general international format
        if not re.match(r'^\+\d{1,4}\s\d{7,15}$', phone):
            return False, "Formato de teléfono inválido. Use el formato: +código país número"

        # Extract country code
        parts = phone.split(' ', 1)
        if len(parts) != 2:
            return False, "Formato de teléfono inválido"

        country_code = parts[0]

        # Check country-specific pattern if available
        if country_code in PHONE_PATTERNS:
            if not re.match(PHONE_PATTERNS[country_code], phone):
                return False, f"Formato incorrecto para {country_code}. Verifica el número de dígitos."

        return True, "Válido"

    def validate_application_data(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate application form data for security and format"""
        errors = []

        # Check required fields
        for field in REQUIRED_FIELDS:
            if not data.get(field) or not data.get(field).strip():
                field_names = {
                    'nombre': 'Nombre',
                    'apellido': 'Apellido',
                    'nacionalidad': 'Nacionalidad',
                    'email': 'Email',
                    'telefono': 'Teléfono',
                    'puesto': 'Puesto',
                    'ingles_nivel': 'Nivel de inglés',
                    'experiencia': 'Experiencia laboral'
                }
                errors.append(f"Campo requerido faltante: {field_names.get(field, field)}")

        # Special validation for phone number
        if 'telefono' in data and data['telefono']:
            is_valid, message = self.validate_phone_number(data['telefono'])
            if not is_valid:
                errors.append(f"Teléfono: {message}")

        # Validate field formats (excluding phone which has special validation)
        for field, pattern in VALIDATION_PATTERNS.items():
            if field == 'telefono':  # Skip phone, already validated above
                continue
            if field in data and data[field]:
                if not re.match(pattern, data[field].strip()):
                    errors.append(f"Formato inválido para {field}")

        # Validate field lengths to prevent DoS
        max_lengths = {
            'nombre': 50, 'apellido': 50, 'email': 100, 'telefono': 25,
            'nacionalidad': 50, 'puesto': 50, 'experiencia': 500,
            'motivacion': 1000, 'disponibilidad': 200, 'puestos_adicionales': 200,
            'espanol_nivel': 20, 'otro_idioma': 50, 'otro_idioma_nivel': 20,
            'ingles_nivel': 20
        }

        for field, max_length in max_lengths.items():
            if field in data and data[field] and len(data[field]) > max_length:
                errors.append(f"Campo {field} excede la longitud máxima de {max_length} caracteres")

        return len(errors) == 0, errors

    def check_duplicate_application(self, email: str) -> bool:
        """Check if an application with this email already exists"""
        try:
            self._ensure_initialized()

            existing = self.collection.find_one({"email": email.lower().strip()})
            return existing is not None
        except Exception as e:
            self.logger.error(f"Error checking duplicate application for {email}: {e}")
            return False  # If we can't check, allow the application

    def validate_file(self, file, field_name: str) -> Tuple[bool, Optional[str], int]:
        """Validate uploaded file size and extension"""
        if not file or not file.filename:
            return True, None, 0

        # Validate file extension
        if field_name in ALLOWED_EXTENSIONS:
            file_extension = file.filename.split('.')[-1].lower() if '.' in file.filename else ''
            if f'.{file_extension}' not in ALLOWED_EXTENSIONS[field_name]:
                allowed = ', '.join(ALLOWED_EXTENSIONS[field_name])
                return False, f"Tipo de archivo no permitido para {field_name}. Permitidos: {allowed}", 0

        # Validate file size
        try:
            file.seek(0, 2)  # Seek to end
            file_size = file.tell()
            file.seek(0)  # Reset to beginning
        except IOError:
            return False, f"Error al procesar el archivo {field_name}", 0

        if field_name in FILE_SIZE_LIMITS and file_size > FILE_SIZE_LIMITS[field_name]:
            max_size_mb = FILE_SIZE_LIMITS[field_name] / (1024 * 1024)
            return False, f"El archivo {field_name} es demasiado grande. Máximo: {max_size_mb}MB", file_size

        return True, None, file_size

    def create_application(self, data: Dict[str, Any], files_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a new application"""
        try:
            # Initialize database if needed
            self._ensure_initialized()

            # Validate input data
            is_valid, errors = self.validate_application_data(data)
            if not is_valid:
                return self.error_response("Validation failed", "ValidationError", {"errors": errors})

            # Check for duplicate email
            if self.check_duplicate_application(data['email']):
                return self.error_response(
                    "Ya existe una aplicación con este email",
                    "DuplicateEmailError"
                )

            # Create Application model instance with required fields
            application = Application(
                nombre=data['nombre'].strip(),
                apellido=data['apellido'].strip(),
                email=data['email'].strip(),
                telefono=data['telefono'].strip(),
                nacionalidad=data['nacionalidad'].strip(),
                puesto=data['puesto'].strip(),
                ingles_nivel=data['ingles_nivel'].strip(),
                experiencia=data['experiencia'].strip(),
                # Optional fields
                puestos_adicionales=data.get('puestos_adicionales', '').strip() if data.get('puestos_adicionales') else None,
                salario_esperado=data.get('salario_esperado', '').strip() if data.get('salario_esperado') else None,
                disponibilidad=data.get('disponibilidad', '').strip() if data.get('disponibilidad') else None,
                motivacion=data.get('motivacion', '').strip() if data.get('motivacion') else None,
                # Files info
                files=files_info if files_info else {}
            )

            # Convert to database format
            app_data = application.to_dict()

            # Insert into database
            result = self.collection.insert_one(app_data)

            # Log successful creation
            self.log_operation("create_application", {
                "application_id": str(result.inserted_id),
                "email": data['email'],
                "puesto": data.get('puesto'),
                "has_files": bool(files_info)
            })

            # Return application with ID
            app_data['_id'] = str(result.inserted_id)
            return self.success_response(app_data, "Application created successfully")

        except DuplicateKeyError:
            return self.error_response(
                "Ya existe una aplicación con este email",
                "DuplicateEmailError"
            )
        except Exception as e:
            return self.handle_error("create_application", e, {"email": data.get('email')})

    def get_applications(self, query_params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get applications with optional filtering and pagination"""
        try:
            self._ensure_initialized()

            query_params = query_params or {}

            # Build MongoDB query
            mongo_query = {}

            # Search functionality
            if query_params.get('search'):
                search_term = query_params['search'].strip()
                mongo_query['$or'] = [
                    {'nombre': {'$regex': search_term, '$options': 'i'}},
                    {'apellido': {'$regex': search_term, '$options': 'i'}},
                    {'email': {'$regex': search_term, '$options': 'i'}},
                    {'telefono': {'$regex': search_term, '$options': 'i'}}
                ]

            # Status filter
            if query_params.get('status'):
                mongo_query['status'] = query_params['status']

            # Position filter
            if query_params.get('puesto'):
                mongo_query['puesto'] = query_params['puesto']

            # English level filter
            if query_params.get('ingles_nivel'):
                mongo_query['ingles_nivel'] = query_params['ingles_nivel']

            # Nationality filter
            if query_params.get('nacionalidad'):
                mongo_query['nacionalidad'] = query_params['nacionalidad']

            # Pagination
            page = max(1, query_params.get('page', 1))
            per_page = min(100, max(1, query_params.get('per_page', 10)))
            skip = (page - 1) * per_page

            # Sorting
            sort_field = query_params.get('sort_by', 'created_at')
            sort_order = -1 if query_params.get('sort_order', 'desc') == 'desc' else 1

            # Execute query
            total = self.collection.count_documents(mongo_query)
            cursor = self.collection.find(mongo_query).sort(sort_field, sort_order).skip(skip).limit(per_page)

            applications = []
            for app in cursor:
                app['_id'] = str(app['_id'])
                applications.append(app)

            # Calculate pagination info
            pages = (total + per_page - 1) // per_page
            has_next = page < pages
            has_prev = page > 1

            result = {
                'applications': applications,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total,
                    'pages': pages,
                    'has_next': has_next,
                    'has_prev': has_prev
                }
            }

            self.log_operation("get_applications", {
                "total_found": total,
                "page": page,
                "filters": mongo_query
            })

            return self.success_response(result, f"Retrieved {len(applications)} applications")

        except Exception as e:
            return self.handle_error("get_applications", e, query_params)

    def get_application_by_id(self, application_id: str) -> Dict[str, Any]:
        """Get a single application by ID"""
        try:
            self._ensure_initialized()

            if not ObjectId.is_valid(application_id):
                return self.error_response("Invalid application ID", "InvalidIdError")

            application = self.collection.find_one({"_id": ObjectId(application_id)})

            if not application:
                return self.error_response("Application not found", "NotFoundError")

            application['_id'] = str(application['_id'])

            self.log_operation("get_application_by_id", {"application_id": application_id})

            return self.success_response(application, "Application retrieved successfully")

        except Exception as e:
            return self.handle_error("get_application_by_id", e, {"application_id": application_id})

    def update_application(self, application_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an application"""
        try:
            self._ensure_initialized()

            if not ObjectId.is_valid(application_id):
                return self.error_response("Invalid application ID", "InvalidIdError")

            # Prepare update data
            update_fields = {}

            # Only allow certain fields to be updated
            allowed_fields = ['status', 'nombre', 'apellido', 'telefono', 'puesto', 'ingles_nivel']
            for field in allowed_fields:
                if field in update_data:
                    update_fields[field] = update_data[field]

            if not update_fields:
                return self.error_response("No valid fields to update", "ValidationError")

            # Add updated timestamp
            update_fields['updated_at'] = datetime.now(timezone.utc)

            # Update in database
            result = self.collection.update_one(
                {"_id": ObjectId(application_id)},
                {"$set": update_fields}
            )

            if result.matched_count == 0:
                return self.error_response("Application not found", "NotFoundError")

            self.log_operation("update_application", {
                "application_id": application_id,
                "updated_fields": list(update_fields.keys())
            })

            return self.success_response({"updated_fields": update_fields}, "Application updated successfully")

        except Exception as e:
            return self.handle_error("update_application", e, {
                "application_id": application_id,
                "update_data": update_data
            })

    def update_application_status(self, application_id: str, new_status: str) -> Dict[str, Any]:
        """Update application status"""
        try:
            self._ensure_initialized()

            if not ObjectId.is_valid(application_id):
                return self.error_response("Invalid application ID", "InvalidIdError")

            # Validate status
            valid_statuses = ['pending', 'reviewed', 'approved', 'rejected', 'contacted', 'interview']
            if new_status.lower() not in valid_statuses:
                return self.error_response(
                    f"Invalid status. Must be one of: {', '.join(valid_statuses)}",
                    "ValidationError"
                )

            # Update in database
            updated_at = datetime.now(timezone.utc)
            result = self.collection.update_one(
                {"_id": ObjectId(application_id)},
                {
                    "$set": {
                        "status": new_status.lower(),
                        "updated_at": updated_at
                    }
                }
            )

            if result.matched_count == 0:
                return self.error_response("Application not found", "NotFoundError")

            self.log_operation("update_application_status", {
                "application_id": application_id,
                "new_status": new_status
            })

            return self.success_response({
                "application_id": application_id,
                "status": new_status.lower(),
                "updated_at": updated_at.isoformat()
            }, "Application status updated successfully")

        except Exception as e:
            return self.handle_error("update_application_status", e, {
                "application_id": application_id,
                "new_status": new_status
            })

    def delete_application(self, application_id: str) -> Dict[str, Any]:

        """Delete an application"""
        try:
            self._ensure_initialized()

            if not ObjectId.is_valid(application_id):
                return self.error_response("Invalid application ID", "InvalidIdError")

            # Get application before deletion for logging
            application = self.collection.find_one({"_id": ObjectId(application_id)})
            if not application:
                return self.error_response("Application not found", "NotFoundError")

            # Delete from database
            result = self.collection.delete_one({"_id": ObjectId(application_id)})

            if result.deleted_count == 0:
                return self.error_response("Application not found", "NotFoundError")

            self.log_operation("delete_application", {
                "application_id": application_id,
                "email": application.get('email'),
                "puesto": application.get('puesto')
            })

            return self.success_response(None, "Application deleted successfully")

        except Exception as e:
            return self.handle_error("delete_application", e, {"application_id": application_id})

    def delete_multiple_applications(self, application_ids: List[str]) -> Dict[str, Any]:
        """Delete multiple applications"""
        try:
            self._ensure_initialized()

            if not application_ids:
                return self.error_response("No application IDs provided", "ValidationError")

            # Validate all IDs
            object_ids = []
            for app_id in application_ids:
                if not ObjectId.is_valid(app_id):
                    return self.error_response(f"Invalid application ID: {app_id}", "InvalidIdError")
                object_ids.append(ObjectId(app_id))

            # Delete applications
            result = self.collection.delete_many({"_id": {"$in": object_ids}})

            self.log_operation("delete_multiple_applications", {
                "requested_count": len(application_ids),
                "deleted_count": result.deleted_count
            })

            return self.success_response({
                "deleted_count": result.deleted_count,
                "requested_count": len(application_ids)
            }, f"Deleted {result.deleted_count} applications successfully")

        except Exception as e:
            return self.handle_error("delete_multiple_applications", e, {
                "application_ids": application_ids
            })

    def get_application_statistics(self) -> Dict[str, Any]:
        """Get application statistics"""
        try:
            self._ensure_initialized()

            # Basic counts
            total_applications = self.collection.count_documents({})
            pending_applications = self.collection.count_documents({"status": "pending"})
            approved_applications = self.collection.count_documents({"status": "approved"})
            rejected_applications = self.collection.count_documents({"status": "rejected"})

            # Today's applications
            today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
            applications_today = self.collection.count_documents({
                "created_at": {"$gte": today_start}
            })

            # This week's applications
            from datetime import timedelta
            week_start = today_start - timedelta(days=today_start.weekday())
            applications_this_week = self.collection.count_documents({
                "created_at": {"$gte": week_start}
            })

            # Popular positions
            pipeline = [
                {"$group": {"_id": "$puesto", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": 10}
            ]
            popular_positions_cursor = self.collection.aggregate(pipeline)
            popular_positions = list(popular_positions_cursor)

            # English levels distribution
            pipeline = [
                {"$group": {"_id": "$ingles_nivel", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]
            english_levels_cursor = self.collection.aggregate(pipeline)
            english_levels_distribution = {
                item['_id']: item['count'] for item in english_levels_cursor
            }

            # Countries distribution
            pipeline = [
                {"$group": {"_id": "$nacionalidad", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": 15}
            ]
            countries_cursor = self.collection.aggregate(pipeline)
            countries_distribution = {
                item['_id']: item['count'] for item in countries_cursor
            }

            stats = {
                "total_applications": total_applications,
                "pending_applications": pending_applications,
                "approved_applications": approved_applications,
                "rejected_applications": rejected_applications,
                "applications_today": applications_today,
                "applications_this_week": applications_this_week,
                "popular_positions": popular_positions,
                "english_levels_distribution": english_levels_distribution,
                "countries_distribution": countries_distribution
            }

            self.log_operation("get_application_statistics", {"total_applications": total_applications})

            return self.success_response(stats, "Statistics retrieved successfully")

        except Exception as e:
            return self.handle_error("get_application_statistics", e)

    def search_applications(self, search_query: str, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Full-text search across applications using MongoDB text index

        Args:
            search_query: Text to search for
            filters: Additional filters (status, position, date range, etc.)
        """
        try:
            self._ensure_initialized()

            # Build query
            query = {}

            # Add text search if provided
            if search_query and search_query.strip():
                query["$text"] = {"$search": search_query}

            # Add filters
            if filters:
                if filters.get('status'):
                    query['status'] = filters['status']

                if filters.get('position'):
                    query['puesto'] = filters['position']

                if filters.get('nationality'):
                    query['nacionalidad'] = filters['nationality']

                if filters.get('english_level'):
                    query['ingles_nivel'] = filters['english_level']

                # Date range filter
                if filters.get('from_date') or filters.get('to_date'):
                    date_filter = {}
                    if filters.get('from_date'):
                        try:
                            from_date = datetime.fromisoformat(filters['from_date'].replace('Z', '+00:00'))
                            date_filter['$gte'] = from_date
                        except ValueError:
                            pass

                    if filters.get('to_date'):
                        try:
                            to_date = datetime.fromisoformat(filters['to_date'].replace('Z', '+00:00'))
                            date_filter['$lte'] = to_date
                        except ValueError:
                            pass

                    if date_filter:
                        query['created_at'] = date_filter

            # Pagination
            page = filters.get('page', 1) if filters else 1
            per_page = min(filters.get('per_page', 20) if filters else 20, 100)
            skip = (page - 1) * per_page

            # Execute search with text score if text search is used
            if "$text" in query:
                projection = {"score": {"$meta": "textScore"}}
                sort = [("score", {"$meta": "textScore"})]
                cursor = self.collection.find(query, projection).sort(sort).skip(skip).limit(per_page)
            else:
                cursor = self.collection.find(query).sort("created_at", -1).skip(skip).limit(per_page)

            applications = []
            for doc in cursor:
                doc['_id'] = str(doc['_id'])
                if 'created_at' in doc and isinstance(doc['created_at'], datetime):
                    doc['created_at'] = doc['created_at'].isoformat()
                applications.append(doc)

            # Get total count
            total = self.collection.count_documents(query)

            self.log_operation("search_applications", {
                "search_query": search_query,
                "filters": filters,
                "results": len(applications)
            })

            return self.success_response({
                "applications": applications,
                "pagination": {
                    "page": page,
                    "per_page": per_page,
                    "total": total,
                    "pages": (total + per_page - 1) // per_page
                },
                "search_query": search_query
            })

        except Exception as e:
            return self.handle_error("search_applications", e)

    def export_applications(self, format: str = 'excel', filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Export applications to CSV or Excel format

        Args:
            format: 'csv' or 'excel'
            filters: Filters to apply (status, date range, position, etc.)
        """
        try:
            self._ensure_initialized()

            # Build query from filters
            query = {}
            if filters:
                if filters.get('status'):
                    query['status'] = filters['status']

                if filters.get('position'):
                    query['puesto'] = filters['position']

                if filters.get('nationality'):
                    query['nacionalidad'] = filters['nationality']

                if filters.get('english_level'):
                    query['ingles_nivel'] = filters['english_level']

                # Date range
                if filters.get('from_date') or filters.get('to_date'):
                    date_filter = {}
                    if filters.get('from_date'):
                        try:
                            from_date = datetime.fromisoformat(filters['from_date'].replace('Z', '+00:00'))
                            date_filter['$gte'] = from_date
                        except ValueError:
                            pass

                    if filters.get('to_date'):
                        try:
                            to_date = datetime.fromisoformat(filters['to_date'].replace('Z', '+00:00'))
                            date_filter['$lte'] = to_date
                        except ValueError:
                            pass

                    if date_filter:
                        query['created_at'] = date_filter

            # Get applications
            cursor = self.collection.find(query).sort("created_at", -1)
            applications = list(cursor)

            if not applications:
                return self.error_response("No applications found with the given filters", "NoDataFound")

            # Convert to pandas DataFrame for easy export
            import pandas as pd
            from io import BytesIO
            import base64

            # Prepare data for export
            export_data = []
            for app in applications:
                export_data.append({
                    'ID': str(app.get('_id', '')),
                    'Nombre': app.get('nombre', ''),
                    'Apellido': app.get('apellido', ''),
                    'Email': app.get('email', ''),
                    'Teléfono': app.get('telefono', ''),
                    'Nacionalidad': app.get('nacionalidad', ''),
                    'Nivel de Inglés': app.get('ingles_nivel', ''),
                    'Puesto': app.get('puesto', ''),
                    'Puestos Adicionales': ', '.join(app.get('puestos_adicionales', [])),
                    'Experiencia': app.get('experiencia', ''),
                    'Estado': app.get('status', 'pending'),
                    'CV URL': app.get('cv_url', ''),
                    'Foto URL': app.get('foto_url', ''),
                    'Fecha de Postulación': app.get('created_at', '').isoformat() if isinstance(app.get('created_at'), datetime) else str(app.get('created_at', ''))
                })

            df = pd.DataFrame(export_data)

            # Generate file based on format
            if format.lower() == 'csv':
                output = BytesIO()
                df.to_csv(output, index=False, encoding='utf-8-sig')  # utf-8-sig for Excel compatibility
                output.seek(0)
                file_content = base64.b64encode(output.read()).decode('utf-8')
                filename = f"applications_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                mimetype = 'text/csv'

            elif format.lower() == 'excel':
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Aplicaciones')

                    # Auto-adjust column widths
                    worksheet = writer.sheets['Aplicaciones']
                    for idx, col in enumerate(df.columns):
                        max_length = max(
                            df[col].astype(str).apply(len).max(),
                            len(col)
                        ) + 2
                        worksheet.column_dimensions[chr(65 + idx)].width = min(max_length, 50)

                output.seek(0)
                file_content = base64.b64encode(output.read()).decode('utf-8')
                filename = f"applications_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

            else:
                return self.error_response("Invalid format. Use 'csv' or 'excel'", "InvalidFormat")

            self.log_operation("export_applications", {
                "format": format,
                "count": len(applications),
                "filters": filters
            })

            return self.success_response({
                "file_content": file_content,
                "filename": filename,
                "mimetype": mimetype,
                "count": len(applications),
                "format": format
            }, f"Exported {len(applications)} applications to {format.upper()}")

        except ImportError as e:
            return self.error_response(
                f"Required library not installed: {str(e)}. Install pandas and openpyxl.",
                "DependencyError"
            )
        except Exception as e:
            return self.handle_error("export_applications", e)

    def get_advanced_filters_options(self) -> Dict[str, Any]:
        """Get available options for advanced filters"""
        try:
            self._ensure_initialized()

            # Get unique values for filters
            nationalities = self.collection.distinct("nacionalidad")
            positions = self.collection.distinct("puesto")
            english_levels = self.collection.distinct("ingles_nivel")
            statuses = self.collection.distinct("status")

            # Get date range
            oldest = self.collection.find_one({}, {"created_at": 1}, sort=[("created_at", 1)])
            newest = self.collection.find_one({}, {"created_at": 1}, sort=[("created_at", -1)])

            min_date = None
            max_date = None
            if oldest and oldest.get('created_at'):
                created_at = oldest.get('created_at')
                min_date = created_at.isoformat() if isinstance(created_at, datetime) else str(created_at)
            if newest and newest.get('created_at'):
                created_at = newest.get('created_at')
                max_date = created_at.isoformat() if isinstance(created_at, datetime) else str(created_at)

            return self.success_response({
                "nationalities": sorted([n for n in nationalities if n]),
                "positions": sorted([p for p in positions if p]),
                "english_levels": sorted([e for e in english_levels if e]),
                "statuses": sorted([s for s in statuses if s]),
                "date_range": {
                    "min": min_date,
                    "max": max_date
                }
            })

        except Exception as e:
            return self.handle_error("get_advanced_filters_options", e)

    def health_check(self) -> Dict[str, Any]:
        """Check service health"""
        try:
            self._ensure_initialized()

            # Test database connection
            self.collection.find_one({}, {"_id": 1})

            return {
                "status": "healthy",
                "database_connected": True,
                "service": "ApplicationService"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "database_connected": False,
                "error": str(e),
                "service": "ApplicationService"
            }
