# =============================================
# VISTAS Y APIS PARA GESTIÓN DE CLIENTES Y DESPACHOS
# =============================================
# Este archivo contiene las vistas principales, APIs y decoradores
# para el manejo de clientes, despachos y pagos en la aplicación Water Delivery.
# Incluye protección de vistas según el tipo de usuario (empresa/conductor),
# lógica de negocio y endpoints para AJAX/JS.

from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.urls import reverse_lazy
from django.db.models import Sum
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from datetime import date, datetime
import json
from .models import Cliente, Despacho, Pago, UbicacionCamion, ConfiguracionRastreo
from .forms import ClienteForm, ClienteEditForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.utils import timezone
from decimal import Decimal
from django.db import models

# Decorador para empresa

def solo_empresa(view_func):
    """
    Permite el acceso solo a usuarios con tipo 'empresa'.
    Si el usuario no es empresa, redirige con mensaje de error.
    """
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated or getattr(request.user, 'tipo_usuario', None) != 'empresa':
            return acceso_denegado_conductor(request)
        return view_func(request, *args, **kwargs)
    return _wrapped_view

# Decorador para conductor

def solo_conductor(view_func):
    """
    Permite el acceso solo a usuarios con tipo 'conductor'.
    Si el usuario no es conductor, redirige con mensaje de error.
    """
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated or getattr(request.user, 'tipo_usuario', None) != 'conductor':
            return acceso_denegado_conductor(request)
        return view_func(request, *args, **kwargs)
    return _wrapped_view

# Función de redirección para accesos denegados

def acceso_denegado_conductor(request):
    """
    Redirige al conductor a la página de nuevo despacho con mensaje de error.
    """
    messages.error(request, 'No tienes permiso para acceder a esta página.')
    return redirect('clientes:nuevo_despacho')

# --- PROTECCIÓN DE VISTAS SEGÚN ROL ---

def solo_empresa_o_api_despacho(view_func):
    """
    Permite acceso solo a empresa o a ciertas APIs de despacho.
    """
    def _wrapped_view(request, *args, **kwargs):
        if hasattr(request.user, 'tipo_usuario') and request.user.tipo_usuario == 'conductor':
            return acceso_denegado_conductor(request)
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def empresa_o_conductor(view_func):
    """
    Permite acceso a usuarios autenticados que sean empresa o conductor.
    """
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated or getattr(request.user, 'tipo_usuario', None) not in ['empresa', 'conductor']:
            return acceso_denegado_conductor(request)
        return view_func(request, *args, **kwargs)
    return _wrapped_view

# --- VISTAS Y APIS ---

@solo_empresa
@login_required
def dashboard(request):
    """
    Vista para el panel de control principal.
    Muestra resumen de clientes activos, deuda total y despachos pendientes.
    """
    from datetime import datetime
    
    total_clientes = Cliente.objects.filter(activo=True).count()
    total_deuda = Cliente.objects.aggregate(Sum('debe_total'))['debe_total__sum'] or 0
    despachos_pendientes = Despacho.objects.filter(entregado=False).count()
    fecha_actual = datetime.now().strftime('%d/%m/%Y %H:%M')
    
    return render(request, 'clientes/dashboard.html', {
        'total_clientes': total_clientes,
        'total_deuda': total_deuda,
        'despachos_pendientes': despachos_pendientes,
        'fecha_actual': fecha_actual,
    })

@solo_empresa
@login_required
def dashboard_despachos(request):
    """
    Vista para el dashboard de despachos diarios (solo empresa).
    """
    return render(request, 'clientes/despacho_nuevo.html')

@empresa_o_conductor
@login_required
def nuevo_despacho(request):
    """
    Vista para crear un nuevo despacho (empresa o conductor).
    """
    return render(request, 'clientes/nuevo_despacho.html')

# APIs necesarias para ambos roles
@login_required
def api_clientes_activos(request):
    """
    API para obtener lista de clientes activos.
    Retorna datos básicos de cada cliente para autocompletar o selección.
    """
    clientes = Cliente.objects.filter(activo=True).values(
        'id', 'nombre', 'apellido', 'direccion', 'telefono'
    )
    
    clientes_list = []
    for cliente in clientes:
        clientes_list.append({
            'id': cliente['id'],
            'nombre': f"{cliente['nombre']} {cliente['apellido']}",
            'direccion': cliente['direccion'],
            'telefono': cliente['telefono']
        })
    
    return JsonResponse({'clientes': clientes_list})

@login_required
def api_despachos_hoy(request):
    """
    API para obtener despachos del día actual.
    Retorna lista de despachos con datos del cliente y estado de entrega.
    """
    hoy = date.today()
    despachos = Despacho.objects.filter(
        fecha__date=hoy
    ).select_related('cliente').order_by('-fecha')
    
    despachos_list = []
    for despacho in despachos:
        despachos_list.append({
            'id': despacho.id,
            'cliente': f"{despacho.cliente.nombre} {despacho.cliente.apellido}",
            'direccion': despacho.cliente.direccion,
            'cantidad': despacho.cantidad_botellones,
            'hora': timezone.localtime(despacho.fecha).strftime('%H:%M'),
            'notas': despacho.notas or '',
            'entregado': despacho.entregado
        })
    
    return JsonResponse({'despachos': despachos_list})

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def api_crear_despacho(request):
    """
    API para crear un nuevo despacho.
    Valida datos, crea el despacho y actualiza el saldo del cliente.
    """
    try:
        data = json.loads(request.body)
        cliente_id = data.get('cliente_id')
        cantidad = int(data.get('cantidad', 1))
        notas = data.get('notas', '')
        # Validar que el cliente existe
        cliente = get_object_or_404(Cliente, id=cliente_id, activo=True)
        # Tomar el precio del cliente
        precio = cliente.precio_botellon
        total = precio * cantidad
        # Crear el despacho
        despacho = Despacho.objects.create(
            cliente=cliente,
            cantidad_botellones=cantidad,
            notas=notas,
            precio_unitario=precio,
            total=total
        )
        # Sumar el total al saldo del cliente
        cliente.saldo += total
        cliente.save()
        return JsonResponse({
            'success': True,
            'message': 'Despacho creado exitosamente',
            'despacho': {
                'id': despacho.id,
                'cliente': f"{cliente.nombre} {cliente.apellido}",
                'cantidad': cantidad,
                'hora': timezone.localtime(despacho.fecha).strftime('%H:%M'),
                'notas': notas,
                'entregado': despacho.entregado
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al crear despacho: {str(e)}'
        }, status=400)

# El resto solo empresa
@empresa_o_conductor
@login_required
def api_crear_cliente(request):
    """API para crear un nuevo cliente"""
    try:
        data = json.loads(request.body)
        nombre = data.get('nombre', '').strip()
        apellido = data.get('apellido', '').strip()
        telefono = data.get('telefono', '').strip()
        direccion = data.get('direccion', '').strip()
        
        # Validaciones básicas
        if not nombre or not direccion:
            return JsonResponse({
                'success': False,
                'message': 'Nombre y dirección son requeridos'
            }, status=400)
        
        # Crear el cliente
        cliente = Cliente.objects.create(
            nombre=nombre,
            apellido=apellido,
            telefono=telefono,
            direccion=direccion
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Cliente creado exitosamente',
            'cliente': {
                'id': cliente.id,
                'nombre': f"{cliente.nombre} {cliente.apellido}",
                'direccion': cliente.direccion,
                'telefono': cliente.telefono
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al crear cliente: {str(e)}'
        }, status=400)

@csrf_exempt
@require_http_methods(["POST"])
@solo_empresa
@login_required
def api_eliminar_despacho(request, despacho_id):
    """API para eliminar un despacho"""
    try:
        despacho = get_object_or_404(Despacho, id=despacho_id)
        cliente = despacho.cliente
        # Restar el total del despacho al saldo del cliente
        cliente.saldo -= despacho.total
        cliente.save()
        despacho.delete()
        return JsonResponse({
            'success': True,
            'message': 'Despacho eliminado exitosamente'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al eliminar despacho: {str(e)}'
        }, status=400)

@csrf_exempt
@require_http_methods(["POST"])
@empresa_o_conductor
@login_required
def api_marcar_entregado(request, despacho_id):
    """API para marcar un despacho como entregado"""
    try:
        despacho = get_object_or_404(Despacho, id=despacho_id)
        if not despacho.entregado:
            despacho.entregado = True
            despacho.save()
        return JsonResponse({
            'success': True,
            'message': 'Despacho marcado como entregado'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al marcar como entregado: {str(e)}'
        }, status=400)

# VISTAS PRINCIPALES MEJORADAS

class ClienteListView(ListView):
    model = Cliente
    template_name = "clientes/lista_clientes.html"
    context_object_name = "clientes"
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or getattr(request.user, 'tipo_usuario', None) != 'empresa':
            return acceso_denegado_conductor(request)
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        # MOSTRAR TODOS LOS CLIENTES (activos e inactivos)
        queryset = Cliente.objects.all()
        
        # Filtro de búsqueda por texto
        buscar = self.request.GET.get('buscar')
        if buscar:
            queryset = queryset.filter(
                Q(nombre__icontains=buscar) |
                Q(apellido__icontains=buscar) |
                Q(telefono__icontains=buscar)
            )
        
        # Filtro por estado/deuda
        filtro = self.request.GET.get('filtro')
        if filtro:
            if filtro == 'activos':
                queryset = queryset.filter(activo=True)
            elif filtro == 'inactivos':
                queryset = queryset.filter(activo=False)
            elif filtro == 'con_deuda':
                queryset = queryset.filter(saldo__gt=0)  # Clientes que deben dinero
            elif filtro == 'saldo_favor':
                queryset = queryset.filter(saldo__lt=0)  # Clientes con saldo a favor
        
        return queryset.order_by('-activo', 'nombre')  # Activos primero

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        clientes = context['clientes']
        clientes_info = []
        for cliente in clientes:
            precio = float(cliente.precio_botellon) if cliente.precio_botellon else 2.5
            saldo = float(cliente.saldo)
            if precio > 0:
                if saldo > 0:
                    botellones = int(round(saldo / precio))
                    botellones_color = 'red'
                elif saldo < 0:
                    botellones = int(round(abs(saldo) / precio))
                    botellones_color = 'green'
                else:
                    botellones = 0
                    botellones_color = 'gray'
            else:
                botellones = 0
                botellones_color = 'gray'
            clientes_info.append({
                'obj': cliente,
                'botellones': botellones,
                'botellones_color': botellones_color,
            })
        context['clientes_info'] = clientes_info
        return context

class ClienteCreateView(CreateView):
    model = Cliente
    form_class = ClienteForm
    template_name = "clientes/nuevo_cliente.html"
    success_url = reverse_lazy('clientes:lista_clientes')
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or getattr(request.user, 'tipo_usuario', None) != 'empresa':
            return acceso_denegado_conductor(request)
        return super().dispatch(request, *args, **kwargs)
    
    def get_initial(self):
        """
        Establece valores iniciales para el formulario.
        Asegura que el precio del botellón tenga el valor por defecto correcto.
        """
        initial = super().get_initial()
        initial['precio_botellon'] = Decimal('2.50')
        return initial
    
    def post(self, request, *args, **kwargs):
        """
        Maneja el envío del formulario POST.
        Asegura que el precio del botellón se procese correctamente.
        """
        # Log para depuración
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"[DEBUG] POST data: {request.POST}")
        
        # Procesar el formulario normalmente
        return super().post(request, *args, **kwargs)
    
    def form_valid(self, form):
        """
        Método que se ejecuta cuando el formulario es válido.
        Asegura que el precio del botellón se guarde correctamente.
        """
        # Log para depuración
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"[DEBUG] form_valid - datos limpios: {form.cleaned_data}")
        logger.info(f"[DEBUG] POST data: {self.request.POST}")
        
        # Obtener el precio del formulario
        precio_form = form.cleaned_data.get('precio_botellon')
        logger.info(f"[DEBUG] Precio del formulario: {precio_form}")
        
        # Llamar al método padre para guardar el cliente
        response = super().form_valid(form)
        
        # Obtener el cliente creado
        cliente = self.object
        logger.info(f"[DEBUG] Cliente creado: {cliente.nombre} {cliente.apellido}, precio: {cliente.precio_botellon}")
        
        # Verificar que el precio se guardó correctamente
        if precio_form and precio_form != Decimal('2.50'):
            # Si se especificó un precio diferente, asegurarse de que se guarde
            if cliente.precio_botellon != precio_form:
                logger.info(f"[DEBUG] Actualizando precio de {cliente.precio_botellon} a {precio_form}")
                cliente.precio_botellon = precio_form
                cliente.save()
        
        # Mostrar mensaje de éxito
        messages.success(
            self.request, 
            f'Cliente "{cliente.nombre} {cliente.apellido}" creado exitosamente con precio de botellón: ${cliente.precio_botellon}'
        )
        
        return response

class ClienteUpdateView(UpdateView):
    model = Cliente
    form_class = ClienteEditForm
    template_name = "clientes/editar_cliente.html"
    success_url = reverse_lazy('clientes:lista_clientes')
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or getattr(request.user, 'tipo_usuario', None) != 'empresa':
            return acceso_denegado_conductor(request)
        return super().dispatch(request, *args, **kwargs)
    def get_object(self, queryset=None):
        cliente = super().get_object(queryset)
        # Recalcular debe_total cada vez que se entra a editar
        despachos_todos = cliente.despacho_set.all()
        total_despachos = despachos_todos.aggregate(total=models.Sum('total'))['total'] or 0
        total_pagos = cliente.pagos.aggregate(total=models.Sum('monto'))['total'] or 0
        cliente.saldo = total_despachos - total_pagos
        if float(cliente.precio_botellon) > 0:
            cliente.debe_total = int(round(float(cliente.saldo) / float(cliente.precio_botellon))) if float(cliente.saldo) > 0 else 0
        else:
            cliente.debe_total = 0
        cliente.save()
        return cliente
    def post(self, request, *args, **kwargs):
        # Manejar desactivación desde la lista
        if "activo" in request.POST and request.POST.get("activo") == "false":
            cliente = self.get_object()
            cliente.activo = False
            cliente.save()
            return redirect(self.success_url)
        return super().post(request, *args, **kwargs)
    def form_valid(self, form):
        response = super().form_valid(form)
        cliente = self.object
        despachos_todos = cliente.despacho_set.all()
        actualizados = 0
        for despacho in despachos_todos:
            despacho.precio_unitario = cliente.precio_botellon
            despacho.total = despacho.precio_unitario * despacho.cantidad_botellones
            despacho.save()
            actualizados += 1
        # Recalcular saldo
        total_despachos = despachos_todos.aggregate(total=models.Sum('total'))['total'] or 0
        total_pagos = cliente.pagos.aggregate(total=models.Sum('monto'))['total'] or 0
        cliente.saldo = total_despachos - total_pagos
        # Recalcular debe_total (botellones adeudados)
        if float(cliente.precio_botellon) > 0:
            cliente.debe_total = int(round(float(cliente.saldo) / float(cliente.precio_botellon))) if float(cliente.saldo) > 0 else 0
        else:
            cliente.debe_total = 0
        cliente.save()
        if actualizados > 0:
            messages.success(self.request, f"Se actualizaron {actualizados} despachos al nuevo precio y se recalculó la deuda.")
        return response
    def get_context_data(self, **kwargs):
        # Comentario detallado: Este método asegura que el template reciba el objeto 'cliente' correctamente.
        context = super().get_context_data(**kwargs)
        context['cliente'] = self.object
        # Log para depuración (aparecerá en consola del servidor)
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"[DEBUG] Contexto en editar_cliente: cliente={self.object} debe_total={self.object.debe_total} saldo={self.object.saldo}")
        return context

class ClienteDetailView(DetailView):
    model = Cliente
    template_name = "clientes/detalle_cliente.html"
    context_object_name = "cliente"
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or getattr(request.user, 'tipo_usuario', None) != 'empresa':
            return acceso_denegado_conductor(request)
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Obtener todos los despachos del cliente ordenados por fecha
        context['despachos'] = self.object.despacho_set.all().order_by('-fecha')
        
        # Estadísticas del cliente
        total_despachos = context['despachos'].count()
        despachos_entregados = context['despachos'].filter(entregado=True).count()
        despachos_pendientes = context['despachos'].filter(entregado=False).count()
        total_botellones = sum(d.cantidad_botellones for d in context['despachos'])
        
        context.update({
            'total_despachos': total_despachos,
            'despachos_entregados': despachos_entregados,
            'despachos_pendientes': despachos_pendientes,
            'total_botellones': total_botellones,
        })
        
        return context

@empresa_o_conductor
@login_required
def marcar_entregado(request, pk):
    if not request.user.is_authenticated or getattr(request.user, 'tipo_usuario', None) != 'empresa':
        return acceso_denegado_conductor(request)
    despacho = get_object_or_404(Despacho, pk=pk)
    if not despacho.entregado:
        despacho.entregado = True
        despacho.save()
    return redirect('clientes:detalle_cliente', pk=despacho.cliente.pk)

class DespachoCreateView(CreateView):
    model = Despacho
    fields = ["cliente", "cantidad_botellones", "notas"]
    template_name = "clientes/nuevo_despacho.html"
    success_url = reverse_lazy('clientes:lista_clientes')
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or getattr(request.user, 'tipo_usuario', None) not in ['empresa', 'conductor']:
            return acceso_denegado_conductor(request)
        return super().dispatch(request, *args, **kwargs)
    def form_valid(self, form):
        cliente = form.cleaned_data['cliente']
        precio = cliente.precio_botellon
        cantidad = form.cleaned_data['cantidad_botellones']
        total = precio * cantidad
        form.instance.precio_unitario = precio
        form.instance.total = total
        response = super().form_valid(form)
        cliente.saldo += total
        cliente.save()
        return response

# NUEVAS FUNCIONES PARA HABILITAR/DESHABILITAR
@login_required
def toggle_cliente_status(request, pk):
    if not request.user.is_authenticated or getattr(request.user, 'tipo_usuario', None) != 'empresa':
        return acceso_denegado_conductor(request)
    """Alternar estado activo/inactivo del cliente"""
    cliente = get_object_or_404(Cliente, pk=pk)
    cliente.activo = not cliente.activo
    cliente.save()
    
    status = "habilitado" if cliente.activo else "deshabilitado"
    # Puedes agregar un mensaje aquí si usas Django messages
    
    return redirect('clientes:lista_clientes')

@require_POST
@solo_empresa
@login_required
def registrar_pago(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    monto = Decimal(request.POST.get('monto', '0'))
    observaciones = request.POST.get('observaciones', '')
    if monto > 0:
        Pago.objects.create(cliente=cliente, monto=monto, observaciones=observaciones)
        cliente.saldo -= monto
        cliente.save()
        messages.success(request, f'Abono de ${monto:.2f} registrado correctamente.')
    else:
        messages.error(request, 'El monto debe ser mayor a 0.')
    return redirect('clientes:detalle_cliente', pk=cliente.id)

@empresa_o_conductor
@login_required
def historial_despachos(request):
    """Vista para mostrar el historial de despachos de los últimos 10 días"""
    return render(request, 'clientes/historial_despachos.html')

def api_despachos_recientes(request):
    if not request.user.is_authenticated or getattr(request.user, 'tipo_usuario', None) != 'empresa':
        return acceso_denegado_conductor(request)
    """API para obtener despachos de los últimos 10 días"""
    from datetime import datetime, timedelta
    from django.db.models import F
    
    fecha_limite = datetime.now() - timedelta(days=10)
    despachos = Despacho.objects.filter(
        fecha__gte=fecha_limite
    ).select_related('cliente').order_by('-fecha')
    
    despachos_por_dia = {}
    for despacho in despachos:
        fecha_str = timezone.localtime(despacho.fecha).strftime('%Y-%m-%d')
        if fecha_str not in despachos_por_dia:
            despachos_por_dia[fecha_str] = {
                'fecha': timezone.localtime(despacho.fecha).strftime('%d/%m/%Y'),  # Formato día/mes/año
                'total_botellones': 0,
                'total_despachos': 0,
                'despachos': []
            }
        
        despachos_por_dia[fecha_str]['total_botellones'] += despacho.cantidad_botellones
        despachos_por_dia[fecha_str]['total_despachos'] += 1
        despachos_por_dia[fecha_str]['despachos'].append({
            'id': despacho.id,
            'cliente': f"{despacho.cliente.nombre} {despacho.cliente.apellido}",
            'direccion': despacho.cliente.direccion,
            'cantidad': despacho.cantidad_botellones,
            'hora': timezone.localtime(despacho.fecha).strftime('%H:%M'),
            'notas': despacho.notas or '',
            'entregado': despacho.entregado
        })
    
    # Convertir a lista ordenada por fecha (sin usar lambda)
    resultado = []
    for fecha_str in sorted(despachos_por_dia.keys(), reverse=True):
        resultado.append(despachos_por_dia[fecha_str])
    
    return JsonResponse({'dias': resultado})

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def api_guardar_ubicacion(request):
    """
    API para guardar la ubicación del camión en tiempo real.
    Recibe latitud, longitud y precisión del GPS del conductor.
    """
    try:
        # Verificar que el usuario sea conductor
        if not hasattr(request.user, 'tipo_usuario') or request.user.tipo_usuario != 'conductor':
            return JsonResponse({
                'success': False,
                'message': 'Solo los conductores pueden actualizar su ubicación'
            }, status=403)
        
        # Parsear datos JSON
        data = json.loads(request.body)
        latitud = data.get('latitud')
        longitud = data.get('longitud')
        precision = data.get('precision', 0)
        timestamp = data.get('timestamp')
        
        # Validar datos requeridos
        if not latitud or not longitud:
            return JsonResponse({
                'success': False,
                'message': 'Latitud y longitud son requeridas'
            }, status=400)
        
        # Desactivar ubicaciones anteriores del conductor
        UbicacionCamion.objects.filter(
            conductor=request.user,
            activo=True
        ).update(activo=False)
        
        # Crear nueva ubicación
        ubicacion = UbicacionCamion.objects.create(
            conductor=request.user,
            latitud=latitud,
            longitud=longitud,
            senal_gps='Buena' if precision < 20 else 'Regular' if precision < 50 else 'Mala',
            activo=True
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Ubicación guardada exitosamente',
            'ubicacion_id': ubicacion.id,
            'timestamp': ubicacion.timestamp.isoformat()
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Datos JSON inválidos'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error interno: {str(e)}'
        }, status=500)

@login_required
def api_conductor_info(request):
    """
    API para obtener la información del conductor conectado.
    """
    try:
        # Verificar que el usuario sea conductor
        if not hasattr(request.user, 'tipo_usuario') or request.user.tipo_usuario != 'conductor':
            return JsonResponse({
                'success': False,
                'message': 'Solo los conductores pueden acceder a esta información'
            }, status=403)
        
        # Obtener información del conductor
        conductor_name = f"{request.user.first_name} {request.user.last_name}".strip()
        if not conductor_name:
            conductor_name = request.user.username
        
        return JsonResponse({
            'success': True,
            'conductor_name': conductor_name,
            'conductor_id': request.user.id,
            'email': request.user.email
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error interno: {str(e)}'
        }, status=500)

@solo_empresa
@login_required
def marcar_pendiente(request, pk):
    despacho = get_object_or_404(Despacho, pk=pk)
    if despacho.entregado:
        despacho.entregado = False
        despacho.save()
        # Recalcular saldo del cliente
        cliente = despacho.cliente
        despachos = cliente.despacho_set.all()
        total_despachos = despachos.aggregate(total=models.Sum('total'))['total'] or 0
        total_pagos = cliente.pagos.aggregate(total=models.Sum('monto'))['total'] or 0
        cliente.saldo = total_despachos - total_pagos
        cliente.save()
        messages.success(request, 'El despacho fue marcado como pendiente.')
    return redirect('clientes:detalle_cliente', pk=despacho.cliente.pk)

@solo_empresa
@login_required
def eliminar_despacho(request, pk):
    despacho = get_object_or_404(Despacho, pk=pk)
    cliente = despacho.cliente
    if request.method == 'POST':
        despacho.delete()
        # Recalcular saldo del cliente
        despachos = cliente.despacho_set.all()
        total_despachos = despachos.aggregate(total=models.Sum('total'))['total'] or 0
        total_pagos = cliente.pagos.aggregate(total=models.Sum('monto'))['total'] or 0
        cliente.saldo = total_despachos - total_pagos
        cliente.save()
        messages.success(request, 'Despacho eliminado correctamente.')
        return redirect('clientes:detalle_cliente', pk=cliente.pk)
    return redirect('clientes:detalle_cliente', pk=cliente.pk)

@empresa_o_conductor
@login_required
def ruta_camion(request):
    """
    Vista para mostrar la ruta del camión en tiempo real.
    Solo accesible para usuarios empresa.
    """
    # Obtener la configuración de rastreo
    configuracion = ConfiguracionRastreo.objects.filter(
        empresa=request.user,
        rastreo_activo=True
    ).first()
    
    # Obtener la última ubicación del conductor asignado
    ultima_ubicacion = None
    if configuracion and configuracion.conductor_asignado:
        ultima_ubicacion = UbicacionCamion.objects.filter(
            conductor=configuracion.conductor_asignado,
            activo=True
        ).order_by('-timestamp').first()
    
    # Obtener despachos pendientes para el conductor
    despachos_pendientes = []
    if configuracion and configuracion.conductor_asignado:
        despachos_pendientes = Despacho.objects.filter(
            entregado=False
        ).order_by('fecha')[:5]
    
    # Estadísticas del día
    hoy = timezone.now().date()
    despachos_hoy = Despacho.objects.filter(
        fecha__date=hoy
    ).count()
    
    despachos_completados = Despacho.objects.filter(
        fecha__date=hoy,
        entregado=True
    ).count()
    
    context = {
        'configuracion': configuracion,
        'ultima_ubicacion': ultima_ubicacion,
        'despachos_pendientes': despachos_pendientes,
        'despachos_hoy': despachos_hoy,
        'despachos_completados': despachos_completados,
    }
    
    return render(request, 'clientes/ruta.html', context)